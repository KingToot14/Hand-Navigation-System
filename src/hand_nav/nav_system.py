import cv2

from hand_nav.hands import Hand

from pynput.keyboard import Key, Controller as KeyController, Listener as KeyListener
from pynput.mouse import Button, Controller as MouseController

class StandardNavSystem:
    def __init__(self):
        pass

#region Standard Hands
class HandGesture(Hand):
    def __init__(self):
        pass

class HandPointer(Hand):
    def __init__(self):
        super().__init__()
        
        self.state = None
        self.mouse = MouseController()
        self.keyboard = KeyController()
        
        self.last_pos = (0, 0)
        
        # speed per 10% of capture distance
        self.move_speed = 200
    
    def interpret_landmarks(self) -> None:
        # handle mouse position
        self.update_mouse_position()
        
        # pass landmarks to states
        if self.test_bent(True, True, True, True, True):
            self.change_state(LeftClickState)
        elif self.test_bent(False, True, True, True, True):
            self.change_state(RightClickState)
        else:
            self.change_state(None)
    
    def draw_hand(self, image):
        image = super().draw_hand(image)
        
        state = "None"
        
        if isinstance(self.state, LeftClickState):
            state = "Left Click"
        elif isinstance(self.state, RightClickState):
            state = "Right Click"
        
        image = cv2.putText(image, state, (6, 20), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 255))
        if self.pos:
            image = cv2.putText(image, f"({self.pos[0]:.2f}, {self.pos[1]:.2f})", (6, 40), 
                                cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 255))
        
        return image
    
    def change_state(self, state: type) -> None:
        if not state:
            if self.state:
                self.state.exit_state()
            self.state = None
            return
        
        if isinstance(self.state, state):
            return
        
        # exit current state if set
        if self.state:
            self.state.exit_state()
        
        self.state = state(self.mouse, self.keyboard)
        self.state.enter_state()
    
    def update_mouse_position(self) -> None:
        if not self.last_pos:
            self.last_pos = self.pos
            return
        
        # move the mouse cursor (x is flipped)
        dx = -(self.pos[0] - self.last_pos[0])
        dy = self.pos[1] - self.last_pos[1]
        
        self.mouse.move(dx * self.move_speed * 10, dy * self.move_speed * 10)
        
        self.last_pos = self.pos

#endregion

#region Pointer States
class State:
    def __init__(self, mouse: MouseController = None, keyboard: KeyController = None):
        self.mouse = mouse
        self.keyboard = keyboard
    
    def enter_state(self) -> None:
        return
    
    def exit_state(self) -> None:
        return

class LeftClickState(State):
    def enter_state(self) -> None:
        self.mouse.press(Button.left)

    def exit_state(self) -> None:
        self.mouse.release(Button.left)

class RightClickState(State):
    def enter_state(self) -> None:
        self.mouse.press(Button.right)

    def exit_state(self) -> None:
        self.mouse.release(Button.right)

#endregion