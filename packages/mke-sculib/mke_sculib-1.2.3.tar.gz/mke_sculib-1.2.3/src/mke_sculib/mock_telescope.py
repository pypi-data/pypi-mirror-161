# mocks the SCU api to a degree as needed for developing

import json
import threading
import time
import copy
import logging
import sys
from io import StringIO

import datetime
import astropy.time
import astropy.units as u
import numpy as np
import pandas as pd
from scipy import interpolate

# logging.basicConfig(format='%(asctime)s - %(name)s - - %(message)s', datefmt='%y-%m-%d %H:%M:%S')
# logging.basicConfig(level=logging.DEBUG)
_log = logging.getLogger("mke_sculib.mock_telescope")
# _log.setLevel('DEBUG')

bands = {'Band 1': 1, 'Band 2': 2, 'Band 3': 3, 'Band 4': 4, 'Band 5a': 5, 'Band 5b': 6, 'Band 5c': 7}

vel_max_az = 3
vel_max_el = 1
vel_max_fi = 8

lims_az = (-270, +270)
lims_el = (15, 90)
lims_fi = (-103.5, +100)

dc_stow_pos = {
    1: dict(el=90, az=-90),
    2: dict(el=90, az=+90)
}

dc_band_positions = {
    1: 99.85156,
    2: -103.4874,
    3: -47.6828,
    4: 10.4436,
    5: -6.3976,
    6: -30.84201,
    7: -22.35018,
}



def _parse_body(body):
    with StringIO(body, newline='\n') as fp:
        df = pd.read_csv(fp, sep=' ', names='time az el capture_flag parallactic_angle'.split(), index_col=False)
    df = df.iloc[:,:-2]
    return df


def _mk_intp(t, v):
    i = np.argsort(t)
    vv = v[i]
    tt = t[i]
    lims = (np.min(vv), np.max(vv))
    limst = (tt[0], tt[-1])

    _log.debug(astropy.time.Time(limst, format='mjd').iso)
    _log.debug(lims)


    f = interpolate.interp1d(tt, vv, fill_value=lims, bounds_error=False)
    fun = lambda t: np.nan if t > tt[-1] else f(t)
    return fun


def limit(v, lim):

    if isinstance(lim, float):
        lim = (-lim, +lim)
    if isinstance(v, float) or isinstance(v, int):
        return max(min(v, lim[1]), lim[0])

    i = v > lim[:,1]
    v[i] = lim[i,1]
    i = v < lim[:,0]
    v[i] = lim[i,0]
    return v


class Telescope():

    
    datalog_cols = ["acu.time.internal_time", "acu.azimuth.p_act", "acu.azimuth.p_set", 
                "acu.elevation.p_act",
                "acu.elevation.p_set",
                "acu.general_management_and_controller.state",
                "acu.stow_pin_controller.azimuth_status",
                "acu.stow_pin_controller.elevation_status",
                "acu.command_arbiter.act_authority", 
                "acu.azimuth.axis_bit_status.abs_active", 
                "acu.elevation.axis_bit_status.abs_active",
                "acu.feed_indexer.p_set", 
                "acu.feed_indexer.p_act", 
                "acu.feed_indexer.state",
                "acu.tracking.tracking_status.tr_valid"]

    def __init__(self, speedup_factor=1, t_start = astropy.time.Time.now(), use_realtime=True, UPDATE_INTERVAL = .2, do_write_history = False):
        self.stop = False
        self.speedup_factor = speedup_factor
        self.UPDATE_INTERVAL = UPDATE_INTERVAL
        self.use_realtime = use_realtime
        self.t_internal = t_start
        self.t_start = t_start
        self.do_write_history = do_write_history

        if self.do_write_history:
            self.history = []
        else:
            self.history = None

        self.faz = None
        self.fel = None

        last_session = int(astropy.time.Time.now().unix) - 1629728852
        self.data = { "acu.time.internal_time": self.t_internal.mjd,
                "acu.azimuth.p_act": 90,
                "acu.azimuth.p_set": 90,
                "acu.elevation.p_act": 90,
                "acu.elevation.p_set": 90,
                "acu.feed_indexer.p_set": dc_band_positions[1],
                "acu.feed_indexer.p_act": dc_band_positions[1],
                "acu.general_management_and_controller.state": "STOWED",
                "acu.stow_pin_controller.azimuth_status": "1",
                "acu.stow_pin_controller.elevation_status": "1",
                "acu.command_arbiter.act_authority": "0",
                "acu.azimuth.axis_bit_status.abs_active": True,
                "acu.elevation.axis_bit_status.abs_active": True,
                "acu.feed_indexer.state": 0,
                "acu.tracking.tracking_status.tr_valid": True,
                "datalogging.currentstate": "STOPPED",
                "datalogging.lastSession": last_session
                }

        self.datalog = {last_session: []}
        self.dataLock = threading.Lock()



        # Dictionary to associate a html command path with a function
        # implementing the action depending on the bpody of the call
        self._commands = {}
        self._commands["acu.dish_management_controller.unstow"] = self.action_unstow
        self._commands["acu.dish_management_controller.stow"] = self.action_stow
        self._commands["acu.command_arbiter.authority"] = self.action_command_authority
        self._commands["acu.azimuth.slew_to_abs_pos"] = self.action_slew
        self._commands["acu.elevation.slew_to_abs_pos"] = self.action_slew
        self._commands["acu.pointing_controller.pointing_correction_toggle"] = self.action_dummy
        self._commands["acu.pointing_controller.set_static_pointing_model_parameters"] = self.action_dummy
        self._commands["acu.pointing_controller.ambient_temperature_correction_setup_values"] = self.action_dummy
        self._commands["acu.dish_management_controller.move_to_band"] = self.action_move_to_band
        self._commands["acu.dish_management_controller.interlock_acknowledge"] = self.action_dummy
        # self._commands["acu.azimuth.activate"] = self.action_dummy
        # self._commands["acu.elevation.activate"] = self.action_dummy
        self._commands["acu.dish_management_controller.set_on_source_threshold"] = self.action_dummy
        self._commands["acu.tracking_controller.reset_program_track"] = self.action_reset_prorgam_track


    def update(self, stepsize=None):
        """
        Move telescope positions
        """
        with self.dataLock:

            t_old = self.t_internal
            if stepsize is not None:
                self.t_internal += u.s * stepsize
                dt = float(stepsize)
            elif self.use_realtime:
                self.t_internal = astropy.time.Time.now()
                dt = (self.t_internal - t_old).to_value('s')  # convert to u.s (seconds)
            else:
                self.t_internal += u.s * self.UPDATE_INTERVAL
                dt = self.UPDATE_INTERVAL


            self.data["acu.time.internal_time"] = self.t_internal.mjd
            
            if self.data["acu.general_management_and_controller.state"] == "TRACK":
                paz = float(self.faz(self.t_internal.mjd))
                pel = float(self.fel(self.t_internal.mjd))

                if np.isnan(paz) or np.isnan(pel):
                    self.data["acu.general_management_and_controller.state"] = 'SIP'
                else:
                    self.data["acu.azimuth.p_set"] = paz
                    self.data["acu.elevation.p_set"] = pel
                    # _log.debug('{} {} {}'.format(self.t_internal.iso, self.data["acu.azimuth.p_set"], self.data["acu.elevation.p_set"]))

            d = self.data["acu.azimuth.p_set"] - self.data["acu.azimuth.p_act"]
            if abs(d) < vel_max_az * dt * self.speedup_factor:
                self.data["acu.azimuth.p_act"] = self.data["acu.azimuth.p_set"]
            else:
                self.data["acu.azimuth.p_act"] += np.sign(d) * vel_max_az * dt * self.speedup_factor
                self.data["acu.azimuth.p_act"] = limit(self.data["acu.azimuth.p_act"], lims_az)

            d = self.data["acu.elevation.p_set"] - self.data["acu.elevation.p_act"]
            if abs(d) < vel_max_az * dt * self.speedup_factor:
                self.data["acu.elevation.p_act"] = self.data["acu.elevation.p_set"]
            else:
                self.data["acu.elevation.p_act"] += np.sign(d) * vel_max_el * dt * self.speedup_factor
                self.data["acu.elevation.p_act"] = limit(self.data["acu.elevation.p_act"], lims_el)

            d = self.data["acu.feed_indexer.p_set"] - self.data["acu.feed_indexer.p_act"]
            if abs(d) < vel_max_az * dt * self.speedup_factor:
                self.data["acu.feed_indexer.p_act"] = self.data["acu.feed_indexer.p_set"]
                self.data["acu.feed_indexer.state"] = 110
            else:
                self.data["acu.feed_indexer.p_act"] += np.sign(d) * vel_max_fi * dt * self.speedup_factor
                self.data["acu.feed_indexer.p_act"] = limit(self.data["acu.feed_indexer.p_act"], lims_fi)
                self.data["acu.feed_indexer.state"] = 130

            if self.data["acu.general_management_and_controller.state"].upper() == "SLEW":
                check_inpos = lambda s, tol: abs(self.data[f"acu.{s}.p_act"] - self.data[f"acu.{s}.p_set"]) < abs(tol)
                if check_inpos('feed_indexer', 0.005) and check_inpos('elevation', 0.005) and check_inpos('azimuth', 0.005):
                    self.data["acu.general_management_and_controller.state"] = 'SIP'


            if self.data['datalogging.lastSession'] not in self.datalog:
                _log.debug('UPDATE: Starting new session with ID: {}'.format(self.data['datalogging.lastSession']))
                self.datalog[self.data['datalogging.lastSession']] = []  

            size_logs = sys.getsizeof(self.datalog) / 1000 / 1000 / 1000 # GB
            if size_logs > 0.5: # Gigabyte
                oldest_log = np.min(list(self.datalog.keys()))
                del self.datalog[oldest_log]
            
            size_hist = sys.getsizeof(self.datalog) / 1000 / 1000 / 1000 # GB
            while size_hist > 0.5: # Gigabyte
                # remove 100 lines at a time
                self.history = self.history[100:]
                size_hist = sys.getsizeof(self.datalog) / 1000 / 1000 / 1000 # GB

            row = [self.t_internal] + [self.data[v] for v in Telescope.datalog_cols if 'internal_time' not in v]
            if self.data['datalogging.currentstate'] == "RECORDING":    
                self.datalog[self.data["datalogging.lastSession"]].append(row)

            if self.do_write_history:
                self.history.append(row)




    def get_log(self, id:int, interval_ms:float=None) -> pd.DataFrame:
        with self.dataLock:
            if id == 'history':
                data = self.history
            else:
                data = self.datalog[id]

            times = [row[0] for row in data]
            values = [[row[0].mjd] + row[1:] for row in data]
            tunix = [tt.unix for tt in times]

            df = pd.DataFrame(values, index=tunix, columns = Telescope.datalog_cols)
        
        if interval_ms is not None:
            dt = interval_ms / 1000

            df = df.sort_index()
            t_new = np.arange(df.index[0], df.index[-1] + dt, dt)
            df2 = df.reindex(t_new)
            # for numerical data
            df2 = df2.interpolate('linear')
            df2 = df2[::-1].interpolate('linear')
            df2 = df2[::-1]

            # for non numerical
            df2 = df2.interpolate('ffill')
            df2 = df2.interpolate('bfill')
            df2.index = [datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%dT%H:%M:%S.%fZ') for t in t_new]
        else:
            df2 = df.copy()
            df2.index = [datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%dT%H:%M:%S.%fZ') for t in df2.index]

        for c in df2.columns:
            if '.p_act' in c or '.p_set' in c:
                df2[c] = df2[c].astype(float)

        
        return df2


    def get(self, key):
        with self.dataLock:
            r = copy.copy(self.data[key])
        return r

    def get_many(self, keys):
        with self.dataLock:
            r = {k: copy.copy(self.data[k]) for k in keys}
        return r

    def set(self, key, value):
        with self.dataLock:
            self.data[key] = value

    def action_activate(self, body):
        self.data["acu.stow_pin_controller.azimuth_status"] = "1"
        self.data["acu.stow_pin_controller.elevation_status"] = "1"
        self.data["acu.general_management_and_controller.state"] = "SIP"

    def action_deactivate(self, body):
        self.data["acu.stow_pin_controller.azimuth_status"] = "0"
        self.data["acu.stow_pin_controller.elevation_status"] = "0"
        self.data["acu.general_management_and_controller.state"] = "STANDBY"


    def action_move_to_band(self, body):
        position = body['params']['action']
        fi_set = dc_band_positions[position]
        self.data["acu.feed_indexer.p_set"] = limit(fi_set, lims_fi)


    def action_unstow(self, body):
        self.data["acu.stow_pin_controller.azimuth_status"] = "1"
        self.data["acu.stow_pin_controller.elevation_status"] = "1"
        self.data["acu.general_management_and_controller.state"] = "SIP"

    def action_reset_prorgam_track(self, body):
        self.data["acu.general_management_and_controller.state"] = "SIP"
        self.data["acu.elevation.p_act"] = self.data["acu.elevation.p_set"]
        self.data["acu.azimuth.p_act"] = self.data["acu.azimuth.p_set"]


    def action_stow(self, body):
        _log.debug("action stow")
        self.data["acu.stow_pin_controller.azimuth_status"] = "3"
        self.data["acu.stow_pin_controller.elevation_status"] = "3"
        self.data["acu.elevation.p_act"] = dc_stow_pos[1]['el']
        self.data["acu.elevation.p_set"] = dc_stow_pos[1]['el']
        self.data["acu.azimuth.p_act"] = dc_stow_pos[1]['az']
        self.data["acu.azimuth.p_set"] = dc_stow_pos[1]['az']
        self.data["acu.general_management_and_controller.state"] = "STOWED"

    def action_command_authority(self, body):
        _log.debug("Command authority action")
        self.data["acu.command_arbiter.act_authority"] = "3"

    def action_slew(self, body):
        _log.debug("action slew")
        if body['path'] == "acu.azimuth.slew_to_abs_pos":
            self.data["acu.azimuth.p_set"] = limit(body['params']["new_axis_absolute_position_set_point"], lims_az)
        elif body['path'] == "acu.elevation.slew_to_abs_pos":
            self.data["acu.elevation.p_set"] = limit(body['params']["new_axis_absolute_position_set_point"], lims_el)
        self.data["acu.general_management_and_controller.state"] = "SLEW"

    def action_dummy(self, body):
        _log.debug("action dummy")
        _log.warning("Dummy action called:\n%s", json.dumps(body, indent=4))

    def program_track(self, body):
        _log.debug("program track")
        with self.dataLock:
            self.data["acu.general_management_and_controller.state"] = "TRACK"
            self.body = _parse_body(body)
            self.faz = _mk_intp(self.body['time'].values, self.body['az'].values)
            self.fel = _mk_intp(self.body['time'].values, self.body['el'].values)

        return dict(status=200, headers={}, body="{}")

    def devices_command(self, body):
        _log.debug("devices command:\n%s", body)
        #body = json.loads(body)
        try:
            with self.dataLock:
                if body['path'] in self._commands:
                    self._commands[body['path']](body)
                else:
                    _log.warning("Unknown command: %s", body['path'])

        except Exception as E:
            _log.error("Exception thrown during command execution")
            _log.exception(E)
            return dict(status=500, headers={'Content-Type': 'application/json'}, body="{}")

        return dict(status=200, headers={'Content-Type': 'application/json'}, body="{}")

    def devices_statusValue(self, args):
        _log.debug("status value")
        if "path" not in args:
            return dict(status=202, headers={'Content-Type': 'application/json'}, body="{}")
        path = args.get("path")
        try:
            value = self.get(path)
        except KeyError:
            value = 'UNKNOWN'

        return dict(status=200, headers={'Content-Type': 'application/json'}, body=json.dumps({"value": value, 'finalValue': value}))

    
    def datalogging_sessions(self, *args):
        _log.debug("sessions")
        with self.dataLock:
            value = [k for k in self.datalog.keys()]
        return dict(status=200, headers={'Content-Type': 'application/json'}, body=json.dumps({"value": value}))

    def datalogging_lastSession(self, *args):
        _log.debug("lastSession")
        value = self.get("datalogging.lastSession")
        return dict(status=200, headers={'Content-Type': 'application/json'}, body=json.dumps({"uuid": value}))

    def datalogging_currentState(self, *args):
        value = self.get("datalogging.currentstate")
        return dict(status=200, headers={'Content-Type': 'application/json'}, body=json.dumps({"state": value}))

    def datalogging_start(self, *args):
        _log.debug("Start data logging")
        
        with self.dataLock:
            self.data["datalogging.lastSession"] += 1
            self.data["datalogging.currentstate"] = "RECORDING"
        _log.debug("New Session ID: {}".format(self.data["datalogging.lastSession"]))

        return dict(status=200, headers={}, body="{}")

    def datalogging_stop(self, *args):
        _log.debug("Stop data logging")
        with self.dataLock:
            self.data["datalogging.currentstate"] = "STOPPED"
            
        return dict(status=200, headers={}, body="{}")

    
    def datalogging_exportSession(self, args):
        _log.debug("Exporting Session")
        if "id" not in args:
            return dict(status=202, headers={'Content-Type': 'application/json'}, body="{}")
        if "interval_ms" not in args:
            return dict(status=202, headers={'Content-Type': 'application/json'}, body="{}")

        session_id = 'history' if args['id'] == 'history' else int(args['id'])
        inteval_ms = None if args['interval_ms'] is None else int(args['interval_ms'])

        if session_id not in self.datalog:
            _log.error(f"Session with ID {session_id} was not found in data log. sessions available are{[k for k in self.datalog.keys()]}")
            return dict(status=404, headers={}, body='session ID not found')

        df = self.get_log(session_id, inteval_ms)
        s = 'StartTime;' + df.index[0] + '\n'
        s += 'EndTime;' + df.index[-1] + '\n'
        s += df.to_csv(sep=';')
        return dict(status=200, headers={}, body=s)


