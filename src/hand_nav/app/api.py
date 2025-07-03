from hand_nav.nav_system import StandardNavSystem
from hand_nav.gamepad_system import GamepadSystem

class Api:
    def __init__(self):
        self.nav_system: StandardNavSystem = None
    
    
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