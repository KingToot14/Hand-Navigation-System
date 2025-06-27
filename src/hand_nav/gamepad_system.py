import vgamepad
from vgamepad import XUSB_BUTTON

from hand_nav.camera_manager import CameraManager
from hand_nav.hands import Hand, HandPair

class GamepadSystem:
    def __init__(self):
        gamepad = vgamepad.VX360Gamepad()
        
        cam_manager = CameraManager(
            pair=HandPair(
                HandGamepad(
                    gamepad,
                    {
                        'button1': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
                        'button2': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
                        'button4': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
                        'button5': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
                    }
                ),
                HandGamepad(
                    gamepad,
                    {
                        'button1': XUSB_BUTTON.XUSB_GAMEPAD_A,
                        'button2': XUSB_BUTTON.XUSB_GAMEPAD_B,
                        'button4': XUSB_BUTTON.XUSB_GAMEPAD_X,
                        'button5': XUSB_BUTTON.XUSB_GAMEPAD_Y,
                    }
                )
            )
        )
        
        cam_manager.start_capture()

#region Hands
class HandGamepad(Hand):
    def __init__(self, gamepad: vgamepad.VX360Gamepad, config: dict = {}):
        self.gamepad = gamepad
        
        self.is_pressed = [False, False, False, False, False]
        
        self.button1 = config.get('button1')
        self.button2 = config.get('button2')
        self.button3 = config.get('button3')
        self.button4 = config.get('button4')
        self.button5 = config.get('button5')
    
    def interpret_landmarks(self):
        pressed_copy = self.is_pressed.copy()
        
        if self.button1 != None and self.f1_bent:
            if not self.is_pressed[0]:
                self.is_pressed[0] = True
                self.gamepad.press_button(self.button1)
        elif self.is_pressed[0]:
            self.is_pressed[0] = False
            self.gamepad.release_button(self.button1)
        
        if self.button2 != None and self.f2_bent:
            if not self.is_pressed[1]:
                self.is_pressed[1] = True
                self.gamepad.press_button(self.button2)
        elif self.is_pressed[1]:
            self.is_pressed[1] = False
            self.gamepad.release_button(self.button2)
        
        if self.button3 != None and self.f3_bent:
            if not self.is_pressed[2]:
                self.is_pressed[2] = True
                self.gamepad.press_button(self.button3)
        elif self.is_pressed[2]:
            self.is_pressed[2] = False
            self.gamepad.release_button(self.button3)
        
        if self.button4 != None and self.f4_bent:
            if not self.is_pressed[3]:
                self.is_pressed[3] = True
                self.gamepad.press_button(self.button4)
        elif self.is_pressed[3]:
            self.is_pressed[3] = False
            self.gamepad.release_button(self.button4)
        
        if self.button5 != None and self.f5_bent:
            if not self.is_pressed[4]:
                self.is_pressed[4] = True
                self.gamepad.press_button(self.button5)
        elif self.is_pressed[4]:
            self.is_pressed[4] = False
            self.gamepad.release_button(self.button5)
        
        if pressed_copy != self.is_pressed:
            self.gamepad.update()

#endregion