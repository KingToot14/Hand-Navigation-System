import os
import multiprocessing as mp

from configparser import ConfigParser
import webview

from hand_nav.util import gamepad_config, main_config
from hand_nav.nav_system import StandardNavSystem
from hand_nav.gamepad_system import GamepadSystem

class Api:
    def __init__(self):
        self.nav_system: StandardNavSystem = None
        self.nav_process: mp.Process = None
        self.nav_string: str = ""

        self.config_navigation: ConfigParser
        self.config_gamepad: ConfigParser = gamepad_config()
        
        self.config: ConfigParser = main_config()
        
        self.window: webview.Window = None
        self.dummy: webview.Window = None
    
    # --- Navigation --- #
    def start_thread(self, system):
        try:
            self.nav_system = system()
            self.nav_system.start()
        finally:
            self.nav_system.close()
    
    def create_dummy(self):
        if not self.window:
            return
        
        # prevents Windows from throttling
        self.dummy = webview.create_window('Dummy', html='', width=10, height=10, x=-200, y=0,
                                      on_top=True, resizable=False, frameless=True, shadow=False)
        
        self.window.events.closed += self.dummy.destroy
    
    def destroy_dummy(self):
        if not self.dummy:
            return
        
        self.dummy.destroy()
        
        # remove old event
        if self.window:
            self.window.events.closed -= self.dummy.destroy
        
        self.dummy = None
    
    def start_navigation(self, system: str):
        self.close_navigation()
        
        self.nav_string = system
        
        # start dummy
        if self.config.get('window', 'use_dummy') == 'True':
            self.create_dummy()
        
        # start process
        if system == 'standard':
            self.nav_process = mp.Process(target=self.start_thread, args=(StandardNavSystem,))
        elif system == 'gamepad':
            self.nav_process = mp.Process(target=self.start_thread, args=(GamepadSystem,))
        
        self.nav_process.start()
        self.nav_process.join()
        
        return {
            'message': 'ok'
        }
    
    def close_navigation(self):
        # clear old dummy
        if self.config.get('window', 'use_dummy') == 'True':
            self.destroy_dummy()
        
        if self.nav_process:
            # terminate process
            self.nav_process.terminate()
            self.nav_process.join()
            self.nav_process.close()
            
            self.nav_process = None
    
    
    # --- Config --- #
    def get_config(self, section, option):
        if not self.config:
            return {
                'message': '[err] Config not loaded'
            }
        
        return {
            'message': str(self.config.get(section, option))
        }
    
    def set_config(self, section, option, value):
        if not self.config:            
            return {
                'message': '[err] Config not loaded'
            }
        
        self.config.set(section, option, value)
        
        with open('config/config.ini', 'w') as file:
            self.config.write(file)
        
        return {
            'message': 'Set successfully'
        }
    
    def gamepad_get_config(self, section, option):
        if not self.config_gamepad:
            return {
                'message': '[err] Config not loaded'
            }
        
        return {
            'message': str(self.config_gamepad.get(section, option))
        }
    
    def gamepad_set_config(self, section, option, value):
        if not self.config_gamepad:            
            return {
                'message': '[err] Config not loaded'
            }
        
        self.config_gamepad.set(section, option, value)
        
        with open('config/gamepad.ini', 'w') as file:
            self.config_gamepad.write(file)
        
        return {
            'message': 'Set successfully'
        }