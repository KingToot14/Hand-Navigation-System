import cv2

from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from hand_nav.util import *

class Hand:
    def __init__(self):
        self.pos = None
        self.landmarks = []
    
    def update_landmarks(self, landmarks: list[NormalizedLandmark]) -> None:
        self.landmarks = landmarks
        
        if not landmarks:
            self.pos = None
            return
        
        # palm points
        self.p1 = landmarks[0]
        self.p2 = landmarks[5]
        self.p3 = landmarks[17]
        
        # calculate new position (avg point)
        self.pos = ((self.p1.x + self.p2.x + self.p3.x) / 3, (self.p1.y + self.p2.y + self.p3.y) / 3)
        
        # fingertips
        self.f1 = landmarks[4]
        self.f2 = landmarks[8]
        self.f3 = landmarks[12]
        self.f4 = landmarks[16]
        self.f5 = landmarks[20]
        
        # check if fingers are bent
        threshold = get_sqr_dist(self.pos, [self.p1.x, self.p1.y])
        
        self.f1_bent = get_sqr_dist(self.pos, [self.f1.x, self.f1.y]) < threshold
        self.f2_bent = get_sqr_dist(self.pos, [self.f2.x, self.f2.y]) < threshold
        self.f3_bent = get_sqr_dist(self.pos, [self.f3.x, self.f3.y]) < threshold
        self.f4_bent = get_sqr_dist(self.pos, [self.f4.x, self.f4.y]) < threshold
        self.f5_bent = get_sqr_dist(self.pos, [self.f5.x, self.f5.y]) < threshold
        
        self.interpret_landmarks()
    
    def interpret_landmarks(self) -> None:
        return
    
    def test_bent(self, b1: bool, b2: bool, b3: bool, b4: bool, b5: bool) -> bool:
        return (
            b1 == self.f1_bent and
            b2 == self.f2_bent and
            b3 == self.f3_bent and
            b4 == self.f4_bent and
            b5 == self.f5_bent
        )
    
    def draw_hand(self, image) -> cv2.typing.MatLike:
        if not self.landmarks:
            return image
        
        # palm points
        image = draw_circle(image, self.p1.x, self.p1.y, (255, 0, 0))
        image = draw_circle(image, self.p2.x, self.p2.y, (255, 0, 0))
        image = draw_circle(image, self.p3.x, self.p3.y, (255, 0, 0))
        
        # center point
        if self.pos:
            image = draw_circle(image, self.pos[0], self.pos[1], (255, 0, 255))
        
        # finger tips
        image = draw_circle(image, self.f1.x, self.f1.y, (0, 0, 255) if self.f1_bent else (0, 255, 0))
        image = draw_circle(image, self.f2.x, self.f2.y, (0, 0, 255) if self.f2_bent else (0, 255, 0))
        image = draw_circle(image, self.f3.x, self.f3.y, (0, 0, 255) if self.f3_bent else (0, 255, 0))
        image = draw_circle(image, self.f4.x, self.f4.y, (0, 0, 255) if self.f4_bent else (0, 255, 0))
        image = draw_circle(image, self.f5.x, self.f5.y, (0, 0, 255) if self.f5_bent else (0, 255, 0))
        
        return image

class HandPair:
    def __init__(self, left_hand: Hand = None, right_hand: Hand = None):
        self.left_hand = left_hand   if left_hand  else Hand()
        self.right_hand = right_hand if right_hand else Hand()
    
    def swap_hands(self) -> None:
        self.left_hand, self.right_hand = self.right_hand, self.left_hand
    
    def update_landmarks(self, results: HandLandmarkerResult) -> None:
        l_updated = False
        r_updated = False
        
        for i in range(len(results.handedness)):
            handedness = results.handedness[i][0]
            
            if handedness.category_name == 'Left':
                self.left_hand.update_landmarks(results.hand_landmarks[i])
                l_updated = True
            elif handedness.category_name == 'Right':
                self.right_hand.update_landmarks(results.hand_landmarks[i])
                r_updated = True
        
        if not l_updated:
            self.left_hand.update_landmarks(None)
        if not r_updated:
            self.right_hand.update_landmarks(None)

    def draw_hands(self, image) -> cv2.typing.MatLike:
        if self.left_hand:
            image = self.left_hand.draw_hand(image)
        if self.right_hand:
            image = self.right_hand.draw_hand(image)
        
        return image