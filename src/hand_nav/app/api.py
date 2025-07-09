import os
from configparser import ConfigParser

from hand_nav.nav_system import StandardNavSystem
from hand_nav.gamepad_system import GamepadSystem

class Api:
    def __init__(self):
        self.nav_system: StandardNavSystem = None

        self.config_navigation: ConfigParser
        self.config_gamepad: ConfigParser = self.gamepad_config()
    
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
    
    # --- Config --- #
    def gamepad_default_config(self):
        config = ConfigParser()
        
        config['bindings'] = {
            'a_button':         'Right Thumb',
            'b_button':         'Right Pointer',
            'x_button':         'Right Ring',
            'y_button':         'Right Pinky',
            'dpad_up':          'Left Thumb',
            'dpad_down':        'Left Pointer',
            'dpad_left':        'Left Ring',
            'dpad_right':       'Left Pinky',
            'start':            'Unbound',
            'back':             'Unbound',
            'l_shoulder':       'Unbound',
            'r_shoulder':       'Unbound',
            'l_stick_up':       'Left Up Movement',
            'l_stick_down':     'Left Down Movement',
            'l_stick_left':     'Left Left Movement',
            'l_stick_right':    'Left Right Movement',
            'l_stick_press':    'Right Up Movement',
            'r_stick_up':       'Right Down Movement',
            'r_stick_down':     'Right Left Movement',
            'r_stick_left':     'Right Right Movement',
            'r_stick_right':    'Unbound',
            'r_stick_press':    'Unbound',
            'l_trigger':        'Unbound',
            'r_trigger':        'Unbound',
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