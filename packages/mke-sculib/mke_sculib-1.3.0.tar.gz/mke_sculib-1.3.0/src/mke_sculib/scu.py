#Feed Indexer tests [316-000000-043]

#Author: P.P.A. Kotze, H. Niehaus, T. Glaubach
#Date: 1/9/2020
#Version: 
#0.1 Initial
#0.2 Update after feedback and correction from HN email dated 1/8/2020
#0.3 Rework scu_get and scu_put to simplify
#0.4 attempt more generic scu_put with either jason payload or simple params, remove payload from feedback function
#0.5 create scu_lib
#0.6 1/10/2020 added load track tables and start table tracking also as debug added 'field' command for old scu
#HN: 13/05/2021 Changed the way file name is defined by defining a start time 
# 1.0 2022-05-26 added stowing / unstowing / taking /releasing command authorithy / (de)activating axis
#                added logging
#                changed the session saving function

#Import of Python available libraries
from astropy.time import Time
import datetime
import time
import requests
import os
from io import StringIO

import numpy as np
import pandas as pd


import mke_sculib.chan_list_acu as chans


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BLACK = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    
def print_color(msg, color=colors.FAIL):
    print(f"{color}{msg}{colors.BLACK}")


    
def logfun(name, msg, color):
    t = datetime.datetime.utcnow().isoformat()[:-4].replace('T', ' ') + 'Z'
    print(f'{color}[{t} - {name}] {msg}{colors.BLACK}')

def getLogger(name):
    def printlog(msg, color=colors.BLACK): 
        return logfun(name, msg, color)
    return printlog


log = getLogger('sculib')


configs_dc = {
    'full': chans.channels_detailed,
    'normal': chans.channels_normal,
    'reduced': chans.channels_reduced,
    'small': chans.channels_small,
    'hn_fi': chans.channels_hn_feed_indexer_sensors,
    'hn_tilt': chans.channels_hn_tilt_sensors,
}


state_dc = {
    0: "Undefined",
    1: "Standby",
    2: "Parked",
    3: "Locked",
    4: "E-Stop",
    6: "Stowed",
    9: "Locked and Stowed (3+9)",
    10: "Activating",
    19: "Deactivating",
    110: "SIP",
    120: "Stop",
    130: "Slew",
    220: "Jog",
    300: "Track",
}

state_dc = {k:v.upper() for k, v in state_dc.items()}
state_dc_inv = {v:k for k, v in state_dc.items()}



class scu():
    def __init__(self, ip='localhost', port='8080', debug=True):
        self.ip = ip
        self.port = str(port)
        self.debug = debug

        self.event_log = {}

    @property
    def is_simulator(self):
        return hasattr(self, 'telescope')

    @property
    def t_internal(self):
        value = self.get_device_status_value(f'acu.time.internal_time')
        return Time(value, format='mjd')
        # return Time.now()

    #Direct SCU webapi functions based on urllib PUT/GET
    def feedback(self, r):
        if self.debug == True:
            log('***Feedback:' +  str(r.request.url) + str(r.request.body))
            log(str(r.reason) + str(r.status_code))
            log("***Text returned:")
            log(r.text)
        elif r.status_code != 200:
            log('***Feedback:' +  str(r.request.url) + str(r.request.body), color=colors.WARNING)
            log(str(r.reason) + str(r.status_code), color=colors.WARNING)
            log("***Text returned:", color=colors.WARNING)
            log(r.text, color=colors.WARNING)
            #log(r.reason, r.status_code)
            #log()

    #	def scu_get(device, params = {}, r_ip = self.ip, r_port = port):
    def scu_get(self, device, params = {}):
        '''This is a generic GET command into http: scu port + folder 
        with params=payload'''
        URL = 'http://' + self.ip + ':' + self.port + device
        if device != '/devices/statusValue':
            self.event_log[datetime.datetime.utcnow()] = 'GET | ' + device

        r = requests.get(url = URL, params = params)
        self.feedback(r)
        r.raise_for_status()
        return r

    def scu_put(self, device, payload = {}, params = {}, data=''):
        '''This is a generic PUT command into http: scu port + folder 
        with json=payload'''
        URL = 'http://' + self.ip + ':' + self.port + device
        self.event_log[datetime.datetime.utcnow()] = 'PUT | ' + device

        r = requests.put(url = URL, json = payload, params = params, data = data)
        self.feedback(r)
        r.raise_for_status()
        return r

    def scu_delete(self, device, payload = {}, params = {}):
        '''This is a generic DELETE command into http: scu port + folder 
        with params=payload'''
        URL = 'http://' + self.ip + ':' + self.port + device
        self.event_log[datetime.datetime.utcnow()] = 'DEL | ' + device

        r = requests.delete(url = URL, json = payload, params = params)
        self.feedback(r)
        r.raise_for_status()
        return r

    #SIMPLE PUTS

    #commands to DMC state - dish management controller
    def interlock_acknowledge_dmc(self):
        log('Acknowledge interlock...')
        self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.interlock_acknowledge'})

    def reset_dmc(self):
        log('reset dmc...')
        self.scu_put('/devices/command', 
            {'path': 'acu.dish_management_controller.reset'})

    def activate_dmc(self):
        log('activate dmc...')
        self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.activate'})

    def deactivate_dmc(self):
        log('deactivate dmc')
        self.scu_put('/devices/command', 
            {'path': 'acu.dish_management_controller.deactivate'})
        
    def move_to_band(self, position):
        bands = {'Band 1': 1, 'Band 2': 2, 'Band 3': 3, 'Band 4': 4, 'Band 5a': 5, 'Band 5b': 6, 'Band 5c': 7}
        log('move to band:' + position)
        if not(isinstance(position, str)):
            self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.move_to_band',
            'params': {'action': position}})
        else:
            self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.move_to_band',
            'params': {'action': bands[position]}})
            
    def move_to_azel(self, az_angle, el_angle, az_vel=3.0, el_vel=1.0):
        """synonym for abs_azel. Moves to an absolute az el position
        with a preset slew rate
        Args:
            az_angle (float): abs AZ angle in degree
            el_angle (float): abs EL angle in degree
        """
        log('abs az: {:.4f} el: {:.4f} (vels: ({:.4f}, {:.4f})'.format(az_angle, el_angle, az_vel, el_vel))

        self.scu_put('/devices/command',
            {'path': 'acu.azimuth.slew_to_abs_pos',
            'params': {'new_axis_absolute_position_set_point': az_angle,
            'new_axis_speed_set_point_for_this_move': az_vel}})    

        self.scu_put('/devices/command',
            {'path': 'acu.elevation.slew_to_abs_pos',
            'params': {'new_axis_absolute_position_set_point': el_angle,
            'new_axis_speed_set_point_for_this_move': el_vel}}) 



    def abs_azel(self, az_angle, el_angle):
        log('abs az: {:.4f} el: {:.4f}'.format(az_angle, el_angle))
        self.scu_put('/devices/command',
            {'path': 'acu.dish_management_controller.slew_to_abs_pos',
            'params': {'new_azimuth_absolute_position_set_point': az_angle,
                'new_elevation_absolute_position_set_point': el_angle}})

    def wait_track_start(self, timeout=600, query_delay=.25):
        self.wait_state("acu.azimuth.state", "TRACK", timeout, query_delay)
        self.wait_state("acu.elevation.state", "TRACK", timeout, query_delay)

    # def wait_track_end(self, timeout=600, query_delay=1.):
    #     # This is to allow logging to continue until the track is completed
    #     log('Waiting for track to finish...')

    #     self.wait_duration(10.0, no_stout=True)  

    #     def tester():
    #         a = self.status_Value("acu.tracking.act_pt_end_index_a")
    #         b = self.status_Value("acu.tracking.act_pt_act_index_a")
    #         return (int(a) - int(b)) > 0
        

    #     self.wait_by_testfun(tester, timeout, query_delay)
    #     log('   -> done')

    def wait_settle(self, axis='all', timeout=600, query_delay=.25, tolerance=0.01):
        """
        alias for waitForStatusValue but mapping 'AZ', 'EL', 'FI' to 'acu.azimuth.p_act'
        'acu.elevation.p_act' and 'acu.feed_indexer.p_act'

        Periodically queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            Value:      value to be reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        
        # assures setpoint has actually been send to acu!
        self.wait_duration(1.0, no_stout=True)  

        dc1 = {
            'az': 'azimuth', 'el': 'elevation', 'fi': 'feed_indexer', 
            'azimuth':'azimuth', 'elevation': 'elevation', 'feed_indexer': 'feed_indexer' }
        
        if axis == 'all':
            self.wait_settle('az')
            self.wait_settle('el')
            self.wait_settle('fi')
            return

        key = dc1[axis.lower()]

        if key == 'feed_indexer':
            path = 'acu.feed_indexer.state'
            self.wait_state(path, "SIP", timeout, query_delay, operator = '<=')
        else:
            value = self.get_device_status_value(f'acu.{key}.p_set')
            self.wait_for_pos(key, value, timeout, query_delay, tolerance)


    def wait_for_pos(self, axis, value, timeout=600, query_delay=.25, tolerance=None):
        """
        alias for waitForStatusValue but mapping 'AZ', 'EL', 'FI' to 'acu.azimuth.p_act'
        'acu.elevation.p_act' and 'acu.feed_indexer.p_act'

        Periodically queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            Value:      value to be reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        dc1 = {
            'az': 'azimuth', 'el': 'elevation', 'fi': 'feed_indexer', 
            'azimuth':'azimuth', 'elevation': 'elevation', 'feed_indexer': 'feed_indexer' }
        
        key = dc1[axis.lower()]
    
        if tolerance is not None:
            path = f'acu.{key}.p_act'
            tester = lambda v: abs(v - value) < abs(tolerance)
        else:
            path = f'acu.{key}.p_act'
            tester = lambda v: v == value

        self.wait_for_status(path, value, tester, timeout, query_delay, tolerance)


    def wait_state(self, path, value, timeout=600, query_delay=.25, operator = '=='):          
        val = value if isinstance(value, int) else state_dc_inv[value]
    
        def tester(v):
            if  isinstance(v, int) or v.isnumeric():
                vv = int(v)    
            else:
                vv = state_dc_inv[v.upper()]

            if operator == '==':   return vv == val
            elif operator == '!=': return vv != val
            elif operator == '<':  return vv <  val
            elif operator == '<=': return vv <= val
            elif operator == '>':  return vv >  val
            elif operator == '>=': return vv >= val
            else: raise Exception(str(operator) + ' is not recognized as a valid operator. Allowed are only ==, !=, <=, >=, <, >')

        self.wait_for_status(path, val, tester, timeout, query_delay)

    def waitForStatusValue(self, path, value, timeout=600, query_delay=.25, tolerance=None):
        """
        alias for wait_for_status
        queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            Value:      value to be reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        self.wait_for_status(path, value, None, timeout=timeout, query_delay=query_delay, tolerance=tolerance)


    def wait_by_testfun(self, tester, timeout=600, query_delay=1.0, no_stout=False):
        """
        Periodically queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            tester:     any test function that returns true, when reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        starttime = time.time()

        self.wait_duration(0.5, no_stout=True)    

        is_first = True
        while time.time() - starttime < timeout:            
            if tester():
                if not no_stout and not is_first:
                    log('  -> done', color=colors.OKBLUE)
                return True
            
            if not no_stout and is_first:
                log('waiting for tester to return true...', color=colors.OKBLUE)
                is_first = False
            self.wait_duration(query_delay, no_stout=True)  

        raise TimeoutError("Sensor: tester() not true after {}s".format(timeout))


    def wait_for_status(self, path, value, tester = None, timeout=600, query_delay=.25, tolerance=None, no_stout=False):
        """
        Periodically queries a device status 'path' until a specific value is reached.

        Args:
            path:       path of the SCU device status
            Value:      value to be reached
            timeout:    Raise TimeoutError after this duration
            query_delay: Period in seconds to wait between two queries.
        """
        starttime = time.time()

        self.wait_duration(0.5, no_stout=True)    

        is_first = True
        while time.time() - starttime < timeout:
            v = self.get_device_status_value(path)
            
            if tester is not None and tester(v):
                if not no_stout and not is_first:
                    log('  -> done', color=colors.OKBLUE)
                return True
            elif tester is None and tolerance is not None and abs(v - value) < abs(tolerance): 
                if not no_stout and not is_first:
                    log('  -> done', color=colors.OKBLUE)
                return True
            elif tester is None and v == value:
                if not no_stout and not is_first:
                    log('  -> done', color=colors.OKBLUE)
                return True

            if not no_stout and is_first:
                if isinstance(value, float):
                    log('wait for {}: {:.3f} (currently at: {:.3f})'.format(path, value, v), color=colors.OKBLUE)
                else:
                    log('wait for {}: {} (currently at: {})'.format(path, value, v), color=colors.OKBLUE)
                is_first = False

            self.wait_duration(query_delay, no_stout=True)  

        raise TimeoutError("Sensor: {} not equal to {} after {}s. Current value: {}".format(path, value, timeout, v))

    def get_device_status_value(self, path):
        """
        Gets one or many device status values (status now)

        Args:
            path:       path of the SCU device status as string, or a list of strings for many
        returns:
            either the value directly or a list of values in case of a list of pathes
        """

        if not isinstance(path, str):
            fun = lambda p: self.scu_get("/devices/statusValue", {"path": p}).json()['value']
            return [fun(p) for p in path]
        else:
            return self.scu_get("/devices/statusValue", {"path": path}).json()['value']
        
    #commands to ACU
    def stow(self):
        log('Stowing...')
        self.scu_put("/devices/command", {"path": "acu.dish_management_controller.stow", "params": {"action": "1"}})

        self.wait_duration(3, no_stout=True)
        self.wait_state("acu.stow_pin_controller.azimuth_status", "LOCKED")
        self.wait_state("acu.stow_pin_controller.elevation_status", "LOCKED")

        
    def unstow(self):
        """
        Unstow both axes
        """
        log('Unstowing...')
        self.scu_put("/devices/command", {"path": "acu.dish_management_controller.unstow"})

        self.wait_duration(3, no_stout=True)      
        self.wait_state("acu.stow_pin_controller.azimuth_status", "STANDBY")
        self.wait_state("acu.stow_pin_controller.elevation_status", "STANDBY")


    def activate_axes(self):
        """
        Activate axes
        """
        self.scu_put("/devices/command", {"path": "acu.azimuth.activate"})
        self.scu_put("/devices/command", {"path": "acu.elevation.activate"})

        self.wait_duration(1, no_stout=True)
        self.waitForStatusValue("acu.azimuth.axis_bit_status.abs_active", True, timeout=10)
        self.waitForStatusValue("acu.elevation.axis_bit_status.abs_active", True, timeout=10)


    def deactivate_axes(self):
        """
        Activate axes
        """
        self.scu_put("/devices/command", {"path": "acu.azimuth.deactivate"})
        self.scu_put("/devices/command", {"path": "acu.elevation.deactivate"})

        self.wait_duration(1, no_stout=True)        
        self.waitForStatusValue("acu.azimuth.axis_bit_status.abs_active", False, timeout=10)
        self.waitForStatusValue("acu.elevation.axis_bit_status.abs_active", False, timeout=10)


    def release_command_authority(self):
        """
        Release command authority.
        """
        log('Releasing Command Authority...')
        self.command_authority('Release')
        self.wait_duration(5)
    
    def get_command_authority(self):
        """
        get command authority.
        """
        log('Getting Command Authority...')


        self.command_authority('Get')
        # # ICD Version 2.4 says 4, but actual behavior of 21.07.2021 is value 3 == SCU
        # self.wait_for_status("acu.command_arbiter.act_authority", "3", timeout=10)
        self.wait_duration(5)
        
    #command authority
    def command_authority(self, action):
        #1 get #2 release
        
        authority={'Get': 1, 'Release': 2}
        self.scu_put('/devices/command', 
            {'path': 'acu.command_arbiter.authority',
            'params': {'action': authority[action]}})
        
    def activate_az(self):
        log('act azimuth')
        self.scu_put('/devices/command', 
            {'path': 'acu.elevation.activate'})

    def activate_el(self):
        log('activate elevation')
        self.scu_put('/devices/command', 
            {'path': 'acu.elevation.activate'})

    def deactivate_el(self):
        log('deactivate elevation')
        self.scu_put('/devices/command', 
            {'path': 'acu.elevation.deactivate'})

    def abs_azimuth(self, az_angle, az_vel):
        log('abs az: {:.4f} vel: {:.4f}'.format(az_angle, az_vel))
        self.scu_put('/devices/command',
            {'path': 'acu.azimuth.slew_to_abs_pos',
            'params': {'new_axis_absolute_position_set_point': az_angle,
            'new_axis_speed_set_point_for_this_move': az_vel}})    

    def abs_elevation(self, el_angle, el_vel):
        log('abs el: {:.4f} vel: {:.4f}'.format(el_angle, el_vel))
        self.scu_put('/devices/command',
            {'path': 'acu.elevation.slew_to_abs_pos',
            'params': {'new_axis_absolute_position_set_point': el_angle,
            'new_axis_speed_set_point_for_this_move': el_vel}}) 

    def load_static_offset(self, az_offset, el_offset):
        log('offset az: {:.4f} el: {:.4f}'.format(az_offset, el_offset))
        self.scu_put('/devices/command',
            {'path': 'acu.tracking_controller.load_static_tracking_offsets.',
            'params': {'azimuth_tracking_offset': az_offset,
                        'elevation_tracking_offset': el_offset}})     #Track table commands


    
    def load_program_track(self, load_type, entries, t=[0]*50, az=[0]*50, el=[0]*50):
        log(load_type)    
        LOAD_TYPES = {
            'LOAD_NEW' : 1, 
            'LOAD_ADD' : 2, 
            'LOAD_RESET' : 3}
        
        #table selector - to tidy for future use
        ptrackA = 11
        
        TABLE_SELECTOR =  {
            'pTrackA' : 11,
            'pTrackB' : 12,
            'oTrackA' : 21,
            'oTrackB' : 22}
        
        #funny thing is SCU wants 50 entries, even for LOAD RESET! or if you send less then you have to pad the table
    
        if entries != 50:
            padding = 50 - entries
            t  += [0] * padding
            az += [0] * padding
            el += [0] * padding

        self.scu_put('/devices/command',
                    {'path': 'acu.dish_management_controller.load_program_track',
                    'params': {'table_selector': ptrackA,
                                'load_mode': LOAD_TYPES[load_type],
                                'number_of_transmitted_program_track_table_entries': entries,
                                'time_0': t[0], 'time_1': t[1], 'time_2': t[2], 'time_3': t[3], 'time_4': t[4], 'time_5': t[5], 'time_6': t[6], 'time_7': t[7], 'time_8': t[8], 'time_9': t[9], 'time_10': t[10], 'time_11': t[11], 'time_12': t[12], 'time_13': t[13], 'time_14': t[14], 'time_15': t[15], 'time_16': t[16], 'time_17': t[17], 'time_18': t[18], 'time_19': t[19], 'time_20': t[20], 'time_21': t[21], 'time_22': t[22], 'time_23': t[23], 'time_24': t[24], 'time_25': t[25], 'time_26': t[26], 'time_27': t[27], 'time_28': t[28], 'time_29': t[29], 'time_30': t[30], 'time_31': t[31], 'time_32': t[32], 'time_33': t[33], 'time_34': t[34], 'time_35': t[35], 'time_36': t[36], 'time_37': t[37], 'time_38': t[38], 'time_39': t[39], 'time_40': t[40], 'time_41': t[41], 'time_42': t[42], 'time_43': t[43], 'time_44': t[44], 'time_45': t[45], 'time_46': t[46], 'time_47': t[47], 'time_48': t[48], 'time_49': t[49],
                                'azimuth_position_0': az[0], 'azimuth_position_1': az[1], 'azimuth_position_2': az[2], 'azimuth_position_3': az[3], 'azimuth_position_4': az[4], 'azimuth_position_5': az[5], 'azimuth_position_6': az[6], 'azimuth_position_7': az[7], 'azimuth_position_8': az[8], 'azimuth_position_9': az[9], 'azimuth_position_10': az[10], 'azimuth_position_11': az[11], 'azimuth_position_12': az[12], 'azimuth_position_13': az[13], 'azimuth_position_14': az[14], 'azimuth_position_15': az[15], 'azimuth_position_16': az[16], 'azimuth_position_17': az[17], 'azimuth_position_18': az[18], 'azimuth_position_19': az[19], 'azimuth_position_20': az[20], 'azimuth_position_21': az[21], 'azimuth_position_22': az[22], 'azimuth_position_23': az[23], 'azimuth_position_24': az[24], 'azimuth_position_25': az[25], 'azimuth_position_26': az[26], 'azimuth_position_27': az[27], 'azimuth_position_28': az[28], 'azimuth_position_29': az[29], 'azimuth_position_30': az[30], 'azimuth_position_31': az[31], 'azimuth_position_32': az[32], 'azimuth_position_33': az[33], 'azimuth_position_34': az[34], 'azimuth_position_35': az[35], 'azimuth_position_36': az[36], 'azimuth_position_37': az[37], 'azimuth_position_38': az[38], 'azimuth_position_39': az[39], 'azimuth_position_40': az[40], 'azimuth_position_41': az[41], 'azimuth_position_42': az[42], 'azimuth_position_43': az[43], 'azimuth_position_44': az[44], 'azimuth_position_45': az[45], 'azimuth_position_46': az[46], 'azimuth_position_47': az[47], 'azimuth_position_48': az[48], 'azimuth_position_49': az[49],
                                'elevation_position_0': el[0], 'elevation_position_1': el[1], 'elevation_position_2': el[2], 'elevation_position_3': el[3], 'elevation_position_4': el[4], 'elevation_position_5': el[5], 'elevation_position_6': el[6], 'elevation_position_7': el[7], 'elevation_position_8': el[8], 'elevation_position_9': el[9], 'elevation_position_10': el[10], 'elevation_position_11': el[11], 'elevation_position_12': el[12], 'elevation_position_13': el[13], 'elevation_position_14': el[14], 'elevation_position_15': el[15], 'elevation_position_16': el[16], 'elevation_position_17': el[17], 'elevation_position_18': el[18], 'elevation_position_19': el[19], 'elevation_position_20': el[20], 'elevation_position_21': el[21], 'elevation_position_22': el[22], 'elevation_position_23': el[23], 'elevation_position_24': el[24], 'elevation_position_25': el[25], 'elevation_position_26': el[26], 'elevation_position_27': el[27], 'elevation_position_28': el[28], 'elevation_position_29': el[29], 'elevation_position_30': el[30], 'elevation_position_31': el[31], 'elevation_position_32': el[32], 'elevation_position_33': el[33], 'elevation_position_34': el[34], 'elevation_position_35': el[35], 'elevation_position_36': el[36], 'elevation_position_37': el[37], 'elevation_position_38': el[38], 'elevation_position_39': el[39], 'elevation_position_40': el[40], 'elevation_position_41': el[41], 'elevation_position_42': el[42], 'elevation_position_43': el[43], 'elevation_position_44': el[44], 'elevation_position_45': el[45], 'elevation_position_46': el[46], 'elevation_position_47': el[47], 'elevation_position_48': el[48], 'elevation_position_49': el[49]}})

    def start_program_track(self, start_time):
        ptrackA = 11
        #interpol_modes
        NEWTON = 0
        SPLINE = 1
        #start_track_modes
        AZ_EL = 1
        RA_DEC = 2
        RA_DEC_SC = 3  #shortcut
        self.scu_put('/devices/command',
                    {'path': 'acu.dish_management_controller.start_program_track',
                    'params' : {'table_selector': ptrackA,
                                'start_time_mjd': start_time,
                                'interpol_mode': SPLINE,
                                'track_mode': AZ_EL }})


    def run_track_table(self, t=None, az=None, el=None, df=None, columns=['time', 'az', 'el'], activate_logging=True):


        self.stop_program_track()
        self.wait_duration(5)
        if activate_logging:
            # start logging for my testrun
            self.start_logger()
        dt_wait = self.upload_track_table(t, az, el, df, columns, wait_for_start=False)
        # wait for track table to finish
        self.wait_duration(dt_wait)
        self.wait_for_pos('az', az[-1], tolerance=0.05, timeout=20)
        self.wait_for_pos('el', el[-1], tolerance=0.05, timeout=20)
        self.stop_logger()
        self.stop_program_track()
        self.wait_duration(5)



    def upload_track_table(self, t=None, az=None, el=None, df=None, columns=['time', 'az', 'el'], wait_for_start=False):
        """convenience funtion to wrap 
                scu.acu_ska_track(scu.format_body(t, az, el))
            in one call
        Args:
            t (iterable of float): time as mjd
            az (iterable of float): azimuth in degree
            el (iterable of float): elevation (alt) in degree
        """
        if t is None and az is None and el is None and df is not None and columns is not None:
            t, az, el = [df[c].values for c in columns]
        
        log('Running Table ({}, {:5.3f}, {:5.3f}) --> ({}, {:5.3f}, {:5.3f})'.format(Time(t[0], format='mjd').datetime, az[0], el[0], Time(t[-1], format='mjd').datetime, az[-1], el[-1]), color=colors.BOLD)
        
        is_mon_increasing = np.all(np.diff(t) > 0)
        if not is_mon_increasing:
            raise Exception('Time vector in tracking table is not monotonically increasing!')

        # hack: Workaround. The SCU ignores tracking tables with <= 50 entries
        if len(t) <= 50:
            log(f'WARNING!: The given tracking table has only {len(t)} entries.', color=colors.WARNING)
            log(f'The SCU has a bug where tracking tables with <=50 samples are silently ignored.', color=colors.WARNING)
            log(f'reinterpolating (piecewise linear) to 120 samples', color=colors.WARNING)

            # interpolate to 120 samples
            tnew = np.linspace(t[0], t[-1], 120)
            az2 = np.interp(tnew, t, az)
            el2 = np.interp(tnew, t, el)

            return self.upload_track_table(tnew, az2, el2, wait_for_start=wait_for_start)


        rows_table = ["{:6.12f} {:3.8f} {:3.8f}".format(ti, azi, eli) for ti, azi, eli in zip(t, az, el)]
        self.acu_ska_track("\n".join(rows_table))
        if wait_for_start:
            self.wait_track_start(timeout=30)

        return Time(t[-1], format='mjd').unix - self.t_internal.unix


    def stop_program_track(self):
        """
        Stop loading program track table - presumably, stops a programmed track
        """

        log("Requesting stop program track")
        self.acu_ska_track_stoploadingtable()
        self.wait_duration(1)
        
        # See E-Mail from Arne, 2021/11/05
        self.scu_put("/devices/command", payload={"path": "acu.tracking_controller.reset_program_track",
                    "params": {"table_selector": "11", "load_mode": "3", "number_of_transmitted_program_track_table_entries": "0"}})

        self.wait_duration(1)


    def acu_ska_track(self, BODY):
        log(f'uploading acu-ska-track with {len(BODY)} char size...')
        return self.scu_put('/acuska/programTrack', data = BODY)
        
    def acu_ska_track_stoploadingtable(self):
        log('acu ska track stop loading table')
        return self.scu_put('/acuska/stopLoadingTable')
        
    def format_tt_line(self, t, az,  el, capture_flag = 1, parallactic_angle = 0.0):
        '''something will provide a time, az and el as minimum
        time must alread be absolute time desired in mjd format
        assumption is capture flag and parallactic angle will not be used'''
        f_str = '{:.12f} {:.6f} {:.6f} {:.0f} {:.6f}\n'.format(float(t), float(az), float(el), capture_flag, float(parallactic_angle))
        return(f_str)

    def format_body(self, t, az, el):
        body = ''
        for i in range(len(t)):
            body += self.format_tt_line(t[i], az[i], el[i])
        return(body)        

    #status get functions goes here
    
    def status_Value(self, sensor):
        r = self.scu_get('/devices/statusValue', 
            {'path': sensor})
        data = r.json()['value']
        #log('value: ', data)
        return(data)

    def status_finalValue(self, sensor):
        #log('get status finalValue: ', sensor)
        r = self.scu_get('/devices/statusValue', 
            {'path': sensor})
        data = r.json()['finalValue']
        #log('finalValue: ', data)
        return(data)

    def commandMessageFields(self, commandPath):
        r = self.scu_get('/devices/commandMessageFields', 
            {'path': commandPath})
        return r

    def statusMessageField(self, statusPath):
        r = self.scu_get('/devices/statusMessageFields', 
            {'deviceName': statusPath})
        return r
    
    #ppak added 1/10/2020 as debug for onsite SCU version
    #but only info about sensor, value itself is murky?
    def field(self, sensor):
        #old field method still used on site
        r = self.scu_get('/devices/field', 
            {'path': sensor})
        #data = r.json()['value']
        data = r.json()
        return(data)
    
    #logger functions goes here

    def create_logger(self, config_name, sensor_list):
        '''
        PUT create a config for logging
        Usage:
        create_logger('HN_INDEX_TEST', hn_feed_indexer_sensors)
        or 
        create_logger('HN_TILT_TEST', hn_tilt_sensors)
        '''
        log('create logger')
        r = self.scu_put('/datalogging/config', 
            {'name': config_name,
            'paths': sensor_list})
        return r

    '''unusual does not take json but params'''
    def start_logger(self, config_name='normal', stop_if_need=True):
        
            # Start data recording
        if stop_if_need and self.logger_state() != 'STOPPED':
            log('WARNING, logger already recording - attempting to stop and start a fresh logger...', color=colors.WARNING)
            self.stop_logger()  
            self.wait_duration(5)

        if self.logger_state() == 'STOPPED':
            log('Starting logger with config: {} ...'.format(config_name))
            r = self.scu_put('/datalogging/start', params='configName=' + config_name)
        else:
            raise Exception(f'Can not start logging, since logging state != "STOPPED" (actual state: "{self.logger_state()}"')

        return r

    def stop_logger(self):
        log('stop logger')
        r = self.scu_put('/datalogging/stop')
        return r

    def logger_state(self):
#        log('logger state ')
        r = self.scu_get('/datalogging/currentState')
        #log(r.json()['state'])
        return(r.json()['state'])

    def logger_configs(self):
        log('logger configs ')
        r = self.scu_get('/datalogging/configs')
        return(r.json())

    def last_session(self):
        '''
        GET last session
        '''
        log('Last sessions ')
        r = self.scu_get('/datalogging/lastSession')
        session = (r.json()['uuid'])
        return(session)
    
    def logger_sessions(self):
        '''
        GET all sessions
        '''
        log('logger sessions ')
        r = self.scu_get('/datalogging/sessions')
        return r

    def session_query(self, id):
        '''
        GET specific session only - specified by id number
        Usage:
        session_query('16')
        '''
        log('logger sessioN query id ')
        r = self.scu_get('/datalogging/session',
            {'id': id})
        return r

    def session_delete(self, id):
        '''
        DELETE specific session only - specified by id number
        Not working - returns response 500
        Usage:
        session_delete('16')
        '''
        log('delete session ')
        r = self.scu_delete('/datalogging/session',
            params= 'id='+id)
        return r

    def session_rename(self, id, new_name):
        '''
        RENAME specific session only - specified by id number and new session name
        Not working
        Works in browser display only, reverts when browser refreshed!
        Usage:
        session_rename('16','koos')
        '''    
        log('rename session ')
        r = self.scu_put('/datalogging/session',
            params = {'id': id, 
                'name' : new_name})
        return r


    def export_session(self, id = 'last', interval_ms=1000):
        '''
        EXPORT specific session - by id and with interval
        output r.text could be directed to be saved to file 
        Usage: 
        export_session('16',1000)
        or export_session('16',1000).text 
        '''
        log('export session ')
        if interval_ms is None and not hasattr(self, 'telescope'):
            interval_ms = 100

        if id == 'last':
            id = self.last_session()

        r = self.scu_get('/datalogging/exportSession',
            params = {'id': id, 
                'interval_ms' : interval_ms})
        return r

    #sorted_sessions not working yet

    def sorted_sessions(self, isDescending = 'True', startValue = '1', endValue = '25', sortBy = 'Name', filterType='indexSpan'):
        log('sorted sessions')
        r = self.scu_get('/datalogging/sortedSessions',
            {'isDescending': isDescending,
            'startValue': startValue,
            'endValue': endValue,
            'filterType': filterType, #STRING - indexSpan|timeSpan,
            'sortBy': sortBy})
        return r
    
    def get_session_as_text(self, interval_ms=1000, session = 'last'):
        '''
        Get session data as CSV after EXPORTing it
        Default interval is 1s
        Default is last recorded session
        if specified no error checking to see if it exists
        Usage: 
        export_session('16',1000)
        or export_session('16',1000).text 
        '''
        
        log('Attempt export of session: {} at rate {} ms'.format(session, interval_ms))
        if session == 'last':
            #get all logger sessions, may be many
            # r = self.logger_sessions()
            #[-1] for end of list, and ['uuid'] to get id of last session in list
            session = self.last_session()
        log('Session id: {} '.format(session))
        file_txt = self.export_session(session, interval_ms).text
        return file_txt

    def get_session_as_df(self, interval_ms=1000, session = 'last'):
        '''
        Get session data as pandas dataframe after EXPORTing it
        Default interval is 1s
        Default is last recorded session
        if specified no error checking to see if it exists
        Usage: 
        export_session('16',1000)
        or export_session('16',1000).text 
        '''
        
        file_txt = self.get_session_as_text(interval_ms=interval_ms, session = session)

        buf = StringIO(file_txt)
        columns = None

        for i in range(100):
            linestart = buf.tell()
            s = buf.readline()
            if s.strip().startswith(';acu.') or s.strip().startswith('Date/Time;acu.'):
                columns = s
                buf.seek(linestart)
                break
        
        if columns is None: 
            raise Exception("The return format of the acu was not recognized. Here is the first 1000 chars:" + file_txt[:1000]) 

        # _log.trace('NSKIP', nskip)
        df = pd.read_csv(buf, sep=';', index_col=0)

        if 'Unnamed: 0' in df:
            df = df.set_index('Unnamed: 0')

        df.index = pd.to_datetime(df.index, errors='coerce')

        return df

                        
    def save_session(self, path_to_save, interval_ms=1000, session = 'last'):
        '''
        Save session data as CSV after EXPORTing it
        Default interval is 1s
        Default is last recorded session
        if specified no error checking to see if it exists
        Usage: 
        export_session('16',1000)
        or export_session('16',1000).text 
        '''
        
        file_txt = self.get_session_as_text(interval_ms, session)

        folder = os.path.dirname(path_to_save)
        if os.path.exists(folder) == 0:
            log(folder + " does not exist. making new dir", color=colors.WARNING)
            os.mkdir(folder)
            
        log(f'Saving Session as log file to: "{path_to_save}"', color=colors.BOLD)    
        with open(path_to_save, 'a+') as f:
            f.write(file_txt)
        
        
    #Simplified one line commands particular to test section being peformed 

    #wait seconds, wait value, wait finalValue
    def wait_duration(self, seconds, no_stout=False):
        if not no_stout:
            log('wait for {:.1f}s'.format(seconds), color=colors.OKBLUE)
        time.sleep(seconds)
        if not no_stout:
            log('  -> done', color=colors.OKBLUE)

    #Simplified track table functions
    

    def start(self, az_start=None, el_start=None, band_start=None, az_speed=3, el_speed=1, send_default_configs=True):

        log('=== INITIATING STARTUP ROUTINE ===', color=colors.BOLD)
        self.get_command_authority()
        self.reset_dmc()
        self.wait_duration(3)
        self.unstow()

        if send_default_configs:
            configs_scu_dc = self.logger_configs()
            configs_scu = [c['name'] for c in configs_scu_dc]
            for k, v in configs_dc.items():
                if k not in configs_scu:
                    log(f'Creating Default Config: {k} with n={len(v)} channels')
                    self.create_logger(k, v)
        
        self.wait_duration(5)
        self.activate_dmc()
        self.wait_duration(5)
        self.activate_axes()
        self.wait_duration(5)

        if band_start is not None:
            self.move_to_band(band_start)
        if az_start is not None:
            self.abs_azimuth(az_start, az_speed)
        if el_start is not None:
            self.abs_elevation(el_start, el_speed)

        if az_start is not None or el_start is not None or band_start is not None:
            self.wait_settle()
            self.wait_duration(3)
        log('=== STARTUP ROUTINE COMPLETED ===', color=colors.BOLD)

    def shutdown(self):

        log('=== INITIATING SHUTDOWN ROUTINE ===', color=colors.BOLD)
        self.stow()
        self.wait_duration(5)
        self.deactivate_axes()
        self.wait_duration(5)
        self.deactivate_dmc()
        self.wait_duration(5)
        self.release_command_authority()
        self.wait_duration(5)

        log('=== SHUTDOWN ROUTINE COMPLETED ===', color=colors.BOLD)

if __name__ == '__main__':
    log("main")
