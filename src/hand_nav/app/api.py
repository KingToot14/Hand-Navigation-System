import os
import multiprocessing as mp

from configparser import ConfigParser

from hand_nav.util import gamepad_config
from hand_nav.nav_system import StandardNavSystem
from hand_nav.gamepad_system import GamepadSystem

class Api:
    def __init__(self):
        self.nav_system: StandardNavSystem = None
        self.nav_process: mp.Process = None

        self.config_navigation: ConfigParser
        self.config_gamepad: ConfigParser = gamepad_config()
    
    # --- Navigation --- #
    def start_thread(self, system):
        try:
            self.nav_system = system()
            self.nav_system.start()
        finally:
            self.nav_system.close()
    
    def start_navigation(self, system: str):
        self.close_navigation()
        
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
        if self.nav_process:
            # terminate process
            self.nav_process.terminate()
            self.nav_process.join()
            self.nav_process.close()
            
            self.nav_process = None
    
    
    # --- Config --- #
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