from hand_nav.nav_system import StandardNavSystem
from hand_nav.gamepad_system import GamepadSystem

if __name__ == "__main__":
    # nav = StandardNavSystem()
    nav = GamepadSystem()
    
    try:
        nav.start()
    finally:
        nav.close()