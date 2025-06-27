import time

import cv2
import tkinter

from hand_nav.camera_manager import CameraManager
from hand_nav.hands import Hand, HandPair, BendState

from pynput.keyboard import Key, Controller as KeyController, Listener as KeyListener
from pynput.mouse import Button, Controller as MouseController

class StandardNavSystem:
    def __init__(self):
        keyboard = KeyController()
        mouse = MouseController()
        
        cam_manager = CameraManager(
            pair=HandPair(
                HandGesture(keyboard),
                HandPointer(keyboard, mouse)
            )
        )
        
        cam_manager.start_capture()

#region Standard Hands
class HandGesture(Hand):
    def __init__(self, keyboard: KeyController = None):
        self.keyboard = keyboard if keyboard else KeyController()
        
        self.is_bent = [False, False, False]

    def interpret_landmarks(self):
        # check shift
        if self.f1_bent:
            if not self.is_bent[0]:
                self.is_bent[0] = True
                self.keyboard.press(Key.shift)
        elif self.is_bent[0]:
            self.is_bent[0] = False
            self.keyboard.release(Key.shift)
        
        # check ctrl
        if self.f2_bent:
            if not self.is_bent[1]:
                self.is_bent[1] = True
                self.keyboard.press(Key.ctrl)
        elif self.is_bent[1]:
            self.is_bent[1] = False
            self.keyboard.release(Key.ctrl)
        
        # check alt
        if self.f3_bent:
            if not self.is_bent[2]:
                self.is_bent[2] = True
                self.keyboard.press(Key.alt)
        elif self.is_bent[2]:
            self.is_bent[2] = False
            self.keyboard.release(Key.alt)

class HandPointer(Hand):
    def __init__(self, keyboard: KeyController = None, mouse: MouseController = None):
        super().__init__()
        
        self.mouse: MouseController = mouse if mouse else MouseController()
        self.keyboard: KeyController = keyboard if keyboard else KeyController()
        self.state: PointerState = NoneState(self, self.mouse, self.keyboard)
        
        self.last_pos: tuple[float, float] = (0, 0)
        
        root = tkinter.Tk()
        self.screen_x = root.winfo_screenwidth()
        self.screen_y = root.winfo_screenheight()
    
    def interpret_landmarks(self) -> None:
        # handle mouse position
        self.state.update_mouse_position()
        
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
        
        self.bend_influence: float = 0.25
                
        # speed per 10% of capture distance
        self.move_speed: float = 400
        
        self.dead_x: float = 0.0
        self.dead_y: float = 0.0
        
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
    
    def get_position_change(self, position: tuple[float, float]) -> tuple[float, float]:
        if not self.hand.last_pos:
            self.hand.last_pos = self.hand.pos
            return
        
        # move the mouse cursor (x is flipped)
        dx = -(position[0] - self.hand.last_pos[0])
        dy = position[1] - self.hand.last_pos[1]
        
        # deadzone
        if abs(dx) < self.dead_x:
            dx = 0
        if abs(dy) < self.dead_y:
            dy = 0
        
        return (dx, dy)
    
    def update_mouse_position(self) -> None:
        dx, dy = self.get_position_change(self.hand.pos)
        
        # adjust sensitivity based on distance
        if self.bend_influence == -1.0:
            min_bend = min(self.hand.f1_bend_dist, self.hand.f2_bend_dist, self.hand.f3_bend_dist, 
                        self.hand.f4_bend_dist, self.hand.f5_bend_dist)
            diff = max(min((min_bend - self.hand.threshold) / self.hand.threshold, 1.0), 0.0)
            
            dx *= diff
            dy *= diff
        
        # adjust sensitivity if pinky is bent
        if self.hand.f5_bent:
            dx *= self.bend_influence
            dy *= self.bend_influence
        
        # move mouse
        self.mouse.move(dx * self.move_speed * 10, dy * self.move_speed * 10)
        
        self.hand.last_pos = (
            self.hand.pos[0] if dx != 0 else self.hand.last_pos[0],
            self.hand.pos[1] if dy != 0 else self.hand.last_pos[1]
        )
    
    def handle_landmarks(self) -> None:
        self.check_exit()
    
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
            'center': CenterState(self.hand, self.mouse, self.keyboard),
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
    def initialize(self):
        self.origin = self.hand.pos
        self.lock_x = 0.01
        self.lock_y = 0.01
        
        self.locked = True
    
    def update_mouse_position(self):
        if not self.origin:
            return
        
        # attempt to unlock (enter drag mode)
        if self.locked:
            dx, dy = self.get_position_change(self.origin)

            if dx >= self.lock_x or dy >= self.lock_y:
                self.locked = False
        else:
            dx, dy = self.get_position_change(self.hand.pos)
            
            # move mouse
            self.mouse.move(dx * self.move_speed * 10, dy * self.move_speed * 10)
        
        self.hand.last_pos = (
            self.hand.pos[0] if dx != 0 else self.hand.last_pos[0],
            self.hand.pos[1] if dy != 0 else self.hand.last_pos[1]
        )
    
    def conditions_met(self):
        return self.hand.test_bent(BendState.EXTEND, BendState.BENT, BendState.EXTEND, BendState.EXTEND, BendState.IGNORE)
    
    def enter_state(self):
        self.mouse.press(Button.left)
    
    def exit_state(self):
        self.mouse.release(Button.left)

class RightClickState(PointerState):
    def handle_landmarks(self):
        self.check_exit()
    
    def conditions_met(self):
        return self.hand.test_bent(BendState.BENT, BendState.EXTEND, BendState.EXTEND, BendState.EXTEND, BendState.IGNORE)
    
    def enter_state(self):
        self.mouse.press(Button.right)
        self.mouse.release(Button.right)

class CenterState(PointerState):
    def update_mouse_position(self):
        self.mouse.position = (self.hand.screen_x / 2.0, self.hand.screen_y / 2.0)
    
    def conditions_met(self):
        return self.hand.test_bent(BendState.BENT, BendState.EXTEND, BendState.BENT, BendState.BENT, BendState.IGNORE)

#endregion