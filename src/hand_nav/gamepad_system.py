from enum import IntEnum
import re

import vgamepad
from vgamepad import XUSB_BUTTON

from hand_nav.util import main_config
from hand_nav.camera_manager import CameraManager
from hand_nav.hands import Hand, HandPair

class GamepadSystem:
    def __init__(self):
        gamepad = vgamepad.VX360Gamepad()
        
        self.cam_manager = CameraManager(
            pair=HandPair(
                HandGamepad(
                    gamepad,
                    True
                    # {
                    #     'button1': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
                    #     'button2': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
                    #     'button4': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
                    #     'button5': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
                    # }
                ),
                HandGamepad(
                    gamepad,
                    False
                    # {
                    #     'button1': XUSB_BUTTON.XUSB_GAMEPAD_A,
                    #     'button2': XUSB_BUTTON.XUSB_GAMEPAD_B,
                    #     'button4': XUSB_BUTTON.XUSB_GAMEPAD_X,
                    #     'button5': XUSB_BUTTON.XUSB_GAMEPAD_Y,
                    # }
                )
            )
        )
    
    def start(self) -> None:
        self.cam_manager.start_capture()
    
    def close(self) -> None:
        self.cam_manager.close()
        self.cam_manager.pair.left_hand.close()
        self.cam_manager.pair.right_hand.close()

#region Hands
class HandGamepad(Hand):
    def __init__(self, gamepad: vgamepad.VX360Gamepad, left: bool, config: dict = None):
        super().__init__()
        
        self.gamepad = gamepad
        
        self.left = False
        self.is_pressed = [False, False, False, False, False]
        self.x_value = 0.0
        self.y_value = 0.0
        
        self.joy_deadzone = 0.01
        
        if not config:
            self.load_config()
        else:
            self.button1 = config.get('button1')
            self.button2 = config.get('button2')
            self.button3 = config.get('button3')
            self.button4 = config.get('button4')
            self.button5 = config.get('button5')
    
    def load_config(self) -> None:
        config: dict = main_config()
        
        mapping: dict = {
            'a_button':      GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_A),
            'b_button':      GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_B),
            'x_button':      GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_X),
            'y_button':      GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_Y),
            'dpad_up':       GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP),
            'dpad_down':     GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN),
            'dpad_left':     GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT),
            'dpad_right':    GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT),
            'start':         GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_START),
            'back':          GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_BACK),
            'l_shoulder':    GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER),
            'r_shoulder':    GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER),
            'l_stick_up':     GamepadStick(self.gamepad, self),
            'l_stick_down':   GamepadStick(self.gamepad, self),
            'l_stick_left':   GamepadStick(self.gamepad, self),
            'l_stick_right':  GamepadStick(self.gamepad, self),
            'l_stick_press': GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB),
            'r_stick_up':     GamepadStick(self.gamepad, self),
            'r_stick_down':   GamepadStick(self.gamepad, self),
            'r_stick_left':   GamepadStick(self.gamepad, self),
            'r_stick_right':  GamepadStick(self.gamepad, self),
            'r_stick_press': GamepadButton(self.gamepad, XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB),
            'l_trigger':    GamepadTrigger(self.gamepad, True),
            'r_trigger':    GamepadTrigger(self.gamepad, False),
        }
        
        self.button1: list[GamepadMapping] = []
        self.button2: list[GamepadMapping] = []
        self.button3: list[GamepadMapping] = []
        self.button4: list[GamepadMapping] = []
        self.button5: list[GamepadMapping] = []
        
        self.up: list[GamepadMapping] = []
        self.down: list[GamepadMapping] = []
        self.left: list[GamepadMapping] = []
        self.right: list[GamepadMapping] = []
        
        pattern = re.compile(r'(Left|Right|Unbound)\s?(.*)')
        
        for key in config['bindings']:
            value: str = config.get('bindings', key)
            
            result: re.Match[str] = pattern.search(value)
            
            # ignore unbound options
            if not result or result.group(1) == 'Unbound':
                continue
            
            # ignore bindings of opposite sides
            if self.left and result.group(1) == 'Right':
                continue
            if not self.left and result.group(1) == 'Left':
                continue
            
            match result.group(2):
                case 'Thumb':
                    self.button1.append(mapping[key])
                case 'Pointer':
                    self.button2.append(mapping[key])
                case 'Middle':
                    self.button3.append(mapping[key])
                case 'Ring':
                    self.button4.append(mapping[key])
                case 'Pinky':
                    self.button5.append(mapping[key])
                case 'Up Movement':
                    self.up.append(mapping[key])
                case 'Down Movement':
                    self.down.append(mapping[key])
                case 'Left Movement':
                    self.left.append(mapping[key])
                case 'Right Movement':
                    self.right.append(mapping[key])
    
    def activate_bindings(self, bindings) -> None:
        bindings: list[GamepadMapping] = bindings
        
        for mapping in bindings:
            if not mapping.activate():
                return
    
    def deactivate_bindings(self, bindings) -> None:
        bindings: list[GamepadMapping] = bindings
        
        for mapping in bindings:
            if not mapping.deactivate():
                return
    
    def interpret_landmarks(self) -> None:
        # fingers
        if self.f1_bent:
            self.activate_bindings(self.button1)
        else:
            self.deactivate_bindings(self.button1)
        
        if self.f2_bent:
            self.activate_bindings(self.button2)
        else:
            self.deactivate_bindings(self.button2)
        
        if self.f3_bent:
            self.activate_bindings(self.button3)
        else:
            self.deactivate_bindings(self.button3)
        
        if self.f4_bent:
            self.activate_bindings(self.button4)
        else:
            self.deactivate_bindings(self.button4)
        
        if self.f5_bent:
            self.activate_bindings(self.button5)
        else:
            self.deactivate_bindings(self.button5)
        
        # movement
        if self.dy < -self.joy_deadzone:
            self.activate_bindings(self.up)
        else:
            self.deactivate_bindings(self.up)
        
        if self.dy > self.joy_deadzone:
            self.activate_bindings(self.down)
        else:
            self.deactivate_bindings(self.down)
        
        if self.dx < -self.joy_deadzone:
            self.activate_bindings(self.left)
        else:
            self.deactivate_bindings(self.left)
        
        if self.dx > self.joy_deadzone:
            self.activate_bindings(self.right)
        else:
            self.deactivate_bindings(self.right)
        
        # push changes
        self.gamepad.update()
    
    def close(self):
        self.gamepad.reset()

class StickInput(IntEnum):
    LEFT_UP = 1
    LEFT_DOWN = 2
    LEFT_LEFT = 3
    LEFT_RIGHT = 4
    RIGHT_UP = 5
    RIGHT_DOWN = 6
    RIGHT_LEFT = 7
    RIGHT_RIGHT = 8

class GamepadMapping:
    def __init__(self, gamepad: vgamepad.VX360Gamepad):
        self.active: bool = False
        self.gamepad = gamepad
    
    def activate(self) -> None:
        if self.active:
            return False
        
        self.active = True
        self.do_activate()
        
        return True
    
    def do_activate(self) -> None:
        return
    
    def deactivate(self) -> None:
        if not self.active:
            return False
        
        self.active = False
        self.do_deactivate()
        
        return True
    
    def do_deactivate(self):
        return

class GamepadButton(GamepadMapping):
    def __init__(self, gamepad: vgamepad.VX360Gamepad, button: XUSB_BUTTON):
        super().__init__(gamepad)
        
        self.button = button
    
    def do_activate(self) -> None:
        self.gamepad.press_button(self.button)
    
    def do_deactivate(self) -> None:
        self.gamepad.release_button(self.button)

class GamepadStick(GamepadMapping):
    def __init__(self, gamepad: vgamepad.VX360Gamepad, hand: HandGamepad):
        super().__init__(gamepad)
        
        self.hand = hand
    
    def do_activate(self) -> None:
        if self.hand.left:
            self.gamepad.left_joystick_float(self.hand.x_value, self.hand.y_value)
        else:
            self.gamepad.right_joystick_float(self.hand.x_value, self.hand.y_value)
        
        # match self.stick:
        #     case StickInput.LEFT_UP:
        #         self.gamepad.left_joystick_float(self.hand.lx_value, self.hand.ly_value)
        #     case StickInput.LEFT_DOWN:
        #         self.gamepad.left_joystick_float(self.hand.lx_value, self.hand.ly_value)
        #     case StickInput.LEFT_LEFT:
        #         self.gamepad.left_joystick_float(self.hand.lx_value, self.hand.ly_value)
        #     case StickInput.LEFT_RIGHT:
        #         self.gamepad.left_joystick_float(self.hand.lx_value, self.hand.ly_value)
        #     case StickInput.RIGHT_UP:
        #         self.gamepad.right_joystick_float(self.hand.rx_value, self.hand.ry_value)
        #     case StickInput.RIGHT_DOWN:
        #         self.gamepad.right_joystick_float(self.hand.rx_value, self.hand.ry_value)
        #     case StickInput.RIGHT_LEFT:
        #         self.gamepad.right_joystick_float(self.hand.rx_value, self.hand.ry_value)
        #     case StickInput.RIGHT_RIGHT:
        #         self.gamepad.right_joystick_float(self.hand.rx_value, self.hand.ry_value)

class GamepadTrigger(GamepadMapping):
    def __init__(self, gamepad: vgamepad.VX360Gamepad, is_left: bool = True):
        super().__init__(gamepad)
        
        self.is_left = is_left
    
    def do_activate(self):
        if self.is_left:
            self.gamepad.left_trigger_float(1.0)
        else:
            self.gamepad.right_trigger_float(1.0)
    
    def do_deactivate(self):
        if self.is_left:
            self.gamepad.left_trigger_float(0.0)
        else:
            self.gamepad.right_trigger_float(0.0)

#endregion