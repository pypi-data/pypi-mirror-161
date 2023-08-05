#Feed Indexer tests [316-000000-043]

#Author: P.P.A. Kotze
#Date: 1/9/2020
#Version: 
#0.1 Initial
#0.2 Update after feedback and correction from HN email dated 1/8/2020
#0.3 Rework scu_get and scu_put to simplify
#0.4 attempt more generic scu_put with either jason payload or simple params, remove payload from feedback function
#0.5 create scu_lib
#0.6 1/10/2020 added load track tables and start table tracking also as debug added 'field' command for old scu


#Import of Python available libraries
import numpy as np
import json
import pandas as pd

from astropy.time import Time
import datetime, pytz

#scu_ip = '10.96.64.10'
# port = '8080'


bands = {'Band 1': 1, 'Band 2': 2, 'Band 3': 3, 'Band 4': 4, 'Band 5a': 5, 'Band 5b': 6, 'Band 5c': 7}      

lims_az = (-270, +270)
lims_el = (15, 90)
lims_fi = (-103.5, +100)

lims = dict(azimuth=lims_az, elevation=lims_el, feed_indexer=lims_fi)


dc_band_positions = {
    1: 99.85156,
    2: -103.4874,
    3: -47.6828,
    4: 10.4436,
    5: -6.3976,
    6: -30.84201,
    7: -22.35018,
}

categories = {'Deactivate': -1,
        'Deactivating': -1,
        'Activate': 1,
        'Activating': 1,
        'Standby': 2,
        'SIP': 3,
        'Slew': 4,
        'Track': 5,
        'Parked': 6,
        'Stowed': 7,
        'Locked': 8,
        'Locked and Stowed': 9,
        'Undefined': 0,
}




# mocks the SCU api to a degree as needed for developing

import json


import time
import astropy

import datetime

from mke_sculib.mock_telescope import Telescope
import mke_sculib.scu as scu
from mke_sculib.scu import log





def get_routes(telescope: Telescope) -> dict:
    dc_routes_get = {
        '/datalogging/currentState': lambda args: telescope.datalogging_currentState(*args),
        '/devices/statusValue': lambda args: telescope.devices_statusValue(args),
        '/datalogging/lastSession': lambda args: telescope.datalogging_lastSession(*args),
        '/datalogging/exportSession': lambda args: telescope.datalogging_exportSession(args),
        '/datalogging/sessions': lambda args: telescope.datalogging_sessions(*args),
    }
    dc_routes_put = {
        '/devices/command': lambda payload, params, data: telescope.devices_command(payload),
        '/datalogging/start': lambda payload, params, data: telescope.datalogging_start(*params),
        '/datalogging/stop': lambda payload, params, data: telescope.datalogging_stop(*params),
        '/acuska/programTrack': lambda payload, params, data: telescope.program_track(data),
    }
    return dict(GET=dc_routes_get, PUT=dc_routes_put)


class MockRequest():
    def __init__(self, url, body) -> None:
        self.url = url
        self.body = body


class MockResponseObject():
    def __init__(self, url, status_code:int, content) -> None:
        self.status_code = status_code
        self._content = content
        self.reason = 'I am a teapod!'
        self.request = MockRequest(url, content)

    def json(self):
        if not isinstance(self._content, str):
            return self._content
        else:
            return json.loads(self._content)

    @property
    def text(self):
        return str(self._content)



class scu_sim(scu.scu):
    def __init__(self, ip='localhost', port='8080', use_realtime=False, debug=True, speedup_factor=1, t_start = astropy.time.Time.now(), UPDATE_INTERVAL = .2):

        self.dc = {}

        self.t_start = t_start.datetime
        self.history = {}
        
        self.t_elapsed = 0

        self.telescope = Telescope( speedup_factor = speedup_factor, 
                                    t_start = t_start, 
                                    use_realtime = use_realtime, 
                                    UPDATE_INTERVAL = UPDATE_INTERVAL, 
                                    do_write_history=True)        

        self.routes = get_routes(self.telescope)


        scu.scu.__init__(self, ip=ip, port=port, debug=debug)


    @property
    def t_internal(self):
        return self.telescope.t_internal


    #	def scu_get(device, params = {}, r_ip = self.ip, r_port = port):
    def scu_get(self, device, params = {}):
        '''This is a generic GET command into http: scu port + folder 
        with params=payload (OVERWRITTEN FOR SIMULATION!)'''
        URL = 'http://' + self.ip + ':' + self.port + device

        if device not in self.routes['GET']:
            r = MockResponseObject(URL, 404, {})
        else:
            fun = self.routes['GET'][device]
            res = fun(params)
            r = MockResponseObject(URL, res['status'], res['body'])

        self.feedback(r)

        return(r)

    def scu_put(self, device, payload = {}, params = {}, data=''):
        '''This is a generic PUT command into http: scu port + folder 
        with json=payload (OVERWRITTEN FOR SIMULATION!)'''
        URL = 'http://' + self.ip + ':' + self.port + device
        if device not in self.routes['PUT']:
            r = MockResponseObject(URL, 404, {})
        else:
            fun = self.routes['PUT'][device]
            res = fun(payload, params, data)
            r = MockResponseObject(URL, res['status'], res['body'])
        self.feedback(r)
        return(r)

    def scu_delete(self, device, payload = {}, params = {}):
        '''This is a generic DELETE command into http: scu port + folder 
        with params=payload (OVERWRITTEN FOR SIMULATION!)'''
        raise NotImplementedError('Not Implemented for a simulator')
        
    #SIMPLE PUTS
    def print_scu(self, *args, **kwargs):
        print('t = {:10.1f}s SCU_SIM: '.format(self.t_elapsed), end='')
        print(*args, **kwargs)

    #wait seconds, wait value, wait finalValue
    def wait_duration(self, seconds, no_stout=False):
        if not no_stout:
            self.print_scu('wait for {:.1f}s'.format(seconds))
        self.t_elapsed += seconds

        # move until n seconds reached
        ti = 0
        while ti < seconds:
            stepsize = min(seconds - ti, self.telescope.UPDATE_INTERVAL)
            # print(ti)
            ti += stepsize
            self.telescope.update(stepsize)
        if not no_stout:
            self.print_scu(' done *')


    def wait_track_end(self, timeout=600, query_delay=1.):
        # This is to allow logging to continue until the track is completed
        log('Waiting for track to finish...')

        self.wait_duration(10.0, no_stout=True)  
        key = "acu.general_management_and_controller.state"
        self.wait_state(key, 'TRACK', timeout, query_delay, operator = '!=')
        log('   -> done')


    def get_history_df(self, interval_ms = None):

        df = self.telescope.get_log('history', interval_ms)
        if 'Unnamed: 0' in df:
            df = df.set_index('Unnamed: 0')

        df.index = pd.to_datetime(df.index, errors='coerce')
        return df


def plot_motion_pyplot(df, xkey='index', figsize=(12, 12), df_tt=None):
    import matplotlib.pyplot as plt

    if df_tt is not None:
        x_tt = Time(df_tt['time'].values, format='mjd').datetime
        df_tt['azimuth'] = df_tt['az']
        df_tt['elevation'] = df_tt['el']

    f, axs = plt.subplots(4, 1, sharex=True, figsize=figsize)

    telescope_axes = 'azimuth elevation feed_indexer'.split()

    if xkey == 'index':
        x = df.index

    ser = df['acu.general_management_and_controller.state']
    # cats = list(categories.keys())

    # raw_cat = pd.Categorical(ser, categories=cats, ordered=False)
    # s = pd.Series(raw_cat)

    ax = axs[0]
    ax.plot(x, ser, '-k')

    # cats_dc = {i:c for i, c in enumerate(cats)}
    
    # ax.set_ylim(-.05, len(cats) + .05)
    # ax.set_yticks(cats)
    # ax.invert_yaxis()
    ax.grid()

    xlims = None
    colors = 'bgr'
    for ax, s, c in zip(axs[1:], telescope_axes, colors):
        setp, actp = f'acu.{s}.p_set', f'acu.{s}.p_act'

        ax.plot(x, df[setp], '-k')
        ax.plot(x, df[actp], '-' + c)

        if df_tt is not None and s in df_tt:
            ax.plot(x_tt, df_tt[s], ':k')

        if xlims is None:
            xlims = ax.get_xlim()

        act_lim_l, act_lim_h  = ax.get_ylim()
        lim_l, lim_h = lims[s]

        if act_lim_l < lim_l:
            ax.fill_between(xlims, act_lim_l, lim_l, color='gray', alpha=0.3)

        if act_lim_h > lim_h:
            ax.fill_between(xlims, act_lim_h, lim_h, color='gray', alpha=0.3)

        if s == 'feed_indexer':
            for v, k in bands.items():
                pos = dc_band_positions[k]
                if act_lim_l < pos < act_lim_h:
                    ax.axhline(y=pos, color='gray', linestyle='--')
                    ax.annotate(v, xy=(1,pos), xytext=(6,0), color='k', 
                    xycoords = ax.get_yaxis_transform(), textcoords="offset points",
                    size=14, va="center")

        ax.set_ylim((act_lim_l, act_lim_h))
        ax.set_ylabel(s + '\n[deg]')
        ax.legend([setp, actp])
    
    ax.set_xlim(xlims)
    ax.set_xlabel('time')
    return axs

if __name__ == '__main__':
   print("main")

        
        
        
