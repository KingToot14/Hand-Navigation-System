import os
from configparser import ConfigParser

from hand_nav.util import gamepad_config
from hand_nav.nav_system import StandardNavSystem
from hand_nav.gamepad_system import GamepadSystem

class Api:
    def __init__(self):
        self.nav_system: StandardNavSystem = None

        self.config_navigation: ConfigParser
        self.config_gamepad: ConfigParser = gamepad_config()
    
    def close_all(self):
        if self.nav_system:
            self.nav_system.close()
    
    # --- Navigation --- #
    def nav_start(self):
        self.nav_close()
        try:
            self.nav_system = StandardNavSystem()
            self.nav_system.start()
            return {
                'message': 'ok'
            }
        except:
            return {
                'message': 'error'
            }
    
    def nav_close(self):
        if self.nav_system:
            self.nav_system.close()
            self.nav_system = None
    
    
    # --- Gamepad --- #
    def gamepad_start(self):
        self.nav_close()
        try:
            self.nav_system = GamepadSystem()
            self.nav_system.start()
            return {
                'message': 'ok'
            }
        except:
            return {
                'message': 'error'
            }
    
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