import os
from configparser import ConfigParser

from hand_nav.nav_system import StandardNavSystem
from hand_nav.gamepad_system import GamepadSystem

class Api:
    def __init__(self):
        self.nav_system: StandardNavSystem = None

        self.config_navigation: ConfigParser
        self.config_gamepad: ConfigParser = self.gamepad_config()
    
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
        self.gamepad_close()
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
    
    def gamepad_close(self):
        if self.nav_system:
            self.nav_system.close()
            self.nav_system = None
    
    # --- Config --- #
    def gamepad_default_config(self):
        config = ConfigParser()
        
        config['bindings.left'] = {
            'button1': "D-Pad Up",
            'button2': "D-Pad Down",
            'button3': '',
            'button4': "D-Pad Left",
            'button5': "D-Pad Right",
        }
        
        config['bindings.right'] = {
            'button1': "A",
            'button2': "B",
            'button3': '',
            'button4': "X",
            'button5': "Y",
        }
        
        return config
    
    def gamepad_config(self):
        config: ConfigParser
        
        if not os.path.exists('config/gamepad.ini'):
            config = self.gamepad_default_config()
        else:
            config = ConfigParser()
            config.read('config/gamepad.ini')
        
        return config
    
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