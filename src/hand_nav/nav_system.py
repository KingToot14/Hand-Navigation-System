import cv2

from enum import Enum

from hand_nav.hands import Hand

class StandardNavSystem:
    def __init__(self):
        pass

#region Standard Hands
class HandGesture(Hand):
    def __init__(self):
        pass

class PointerState(Enum):
    NONE = 0
    LEFT_CLICK = 1
    RIGHT_CLICK = 2

class HandPointer(Hand):
    def __init__(self):
        self.state = PointerState.NONE
    
    def interpret_landmarks(self) -> None:
        if self.test_bent(True, True, True, True, True):
            self.state = PointerState.LEFT_CLICK
        elif self.test_bent(False, True, True, True, True):
            self.state = PointerState.RIGHT_CLICK
        else:
            self.state = PointerState.NONE
    
    def draw_hand(self, image):
        image = super().draw_hand(image)
        
        state = "None"
        
        if self.state == PointerState.LEFT_CLICK:
            state = "Left Click"
        elif self.state == PointerState.RIGHT_CLICK:
            state = "Right Click"
        
        image = cv2.putText(image, state, (6, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255))
        
        return image

#endregion