import time

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
        
        self.mouse: MouseController = MouseController()
        self.keyboard: KeyController = KeyController()
        self.state: PointerState = NoneState(self, self.mouse, self.keyboard)
        
        self.last_pos: tuple[float, float] = (0, 0)
        
        # speed per 10% of capture distance
        self.move_speed: float = 400
        
        self.dead_x: float = 0.0
        self.dead_y: float = 0.0
    
    def interpret_landmarks(self) -> None:
        # handle mouse position
        self.update_mouse_position()
        
        # pass landmarks to states
        self.state.handle_landmarks()
    
    def draw_hand(self, image):
        image = super().draw_hand(image)
        
        state: str = "None"
        
        if isinstance(self.state, LeftClickState):
            state = "Left Click"
        elif isinstance(self.state, RightClickState):
            state = "Right Click"
        
        image = cv2.putText(image, state, (6, 20), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 255))
        if self.pos:
            image = cv2.putText(image, f"({self.pos[0]:.2f}, {self.pos[1]:.2f})", (6, 40), 
                                cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 255))
        
        return image
    
    def change_state(self, state) -> None:
        self.state = state
        
        self.state.enter_state()
    
    def update_mouse_position(self) -> None:
        if not self.last_pos:
            self.last_pos = self.pos
            return
        
        # move the mouse cursor (x is flipped)
        dx = -(self.pos[0] - self.last_pos[0])
        dy = self.pos[1] - self.last_pos[1]
        
        # deadzone
        if abs(dx) < self.dead_x:
            dx = 0
        if abs(dy) < self.dead_y:
            dy = 0
        
        # adjust sensitivity based on distance
        min_bend = min(self.f1_bend_dist, self.f2_bend_dist, self.f3_bend_dist, self.f4_bend_dist, self.f5_bend_dist)
        diff = max(min((min_bend - self.threshold) / self.threshold, 1.0), 0.0)
        
        dx *= diff
        dy *= diff
        
        # move mouse
        self.mouse.move(dx * self.move_speed * 10, dy * self.move_speed * 10)
        
        self.last_pos = (
            self.pos[0] if dx != 0 else self.last_pos[0],
            self.pos[1] if dy != 0 else self.last_pos[1]
        )

#endregion

#region Pointer States
class PointerState:
    def __init__(self, hand: HandPointer, mouse: MouseController, keyboard: KeyController):
        self.hand: HandPointer = hand
        self.mouse: MouseController = mouse
        self.keyboard: KeyController = keyboard
        
        # delay between switching states
        self.enter_delay: float = 0.05
        self.exit_delay: float = 0.05
        
        self.exit_time: float = 0.0
        self.exiting: bool = False
        
        self.initialize()
    
    def initialize(self) -> None:
        return
    
    def check_exit(self) -> None:
        if self.conditions_met():
            self.exiting = False
            return
        
        # if just started exiting, start a timer
        if not self.exiting:
            self.exit_time = time.time()
            self.exiting = True
        
        # if enough time has passed, exit state
        if time.time() - self.exit_time >= self.exit_delay:
            self.exit_state()
            self.hand.change_state(NoneState(self.hand, self.mouse, self.keyboard))
    
    def handle_landmarks(self) -> None:
        pass
    
    def conditions_met(self) -> bool:
        return True
    
    def enter_state(self) -> None:
        return
    
    def exit_state(self) -> None:
        return

class NoneState(PointerState):
    def initialize(self):
        self.states: dict[str, PointerState] = {
            'left_click': LeftClickState(self.hand, self.mouse, self.keyboard),
            'right_click': RightClickState(self.hand, self.mouse, self.keyboard),
        }
        
        self.curr_state = 'none'
        self.curr_time = 0
    
    def handle_landmarks(self) -> None:
        valid_state = False
        
        # check for a new state to switch to
        for state in self.states:
            if not self.states[state].conditions_met():
                continue
            
            valid_state = True
            
            if self.curr_state != state:
                self.curr_state = state
                self.curr_time = time.time()
            else:
                if time.time() - self.curr_time >= self.states[state].enter_delay:
                    self.hand.change_state(self.states[state])
        
        if not valid_state:
            self.state = 'none'

class LeftClickState(PointerState):
    def handle_landmarks(self):
        self.check_exit()
    
    def conditions_met(self):
        return self.hand.test_bent(True, True, True, True, True)
    
    def enter_state(self):
        self.mouse.press(Button.left)
    
    def exit_state(self):
        self.mouse.release(Button.left)

class RightClickState(PointerState):
    def handle_landmarks(self):
        self.check_exit()
    
    def conditions_met(self):
        return self.hand.test_bent(False, True, True, True, True)
    
    def enter_state(self):
        self.mouse.press(Button.right)
    
    def exit_state(self):
        self.mouse.release(Button.right)

#endregion