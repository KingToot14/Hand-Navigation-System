import enum

import cv2
import tkinter

from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from hand_nav.util import *

class BendState(enum.IntEnum):
    EXTEND = 0
    BENT = 1
    IGNORE = 2

class Hand:
    def __init__(self):
        self.last_pos = None
        self.pos = None
        
        self.landmarks = []
        
        # anchor points
        self.anchor_movement: float = 0.05
        self.anchor_points: int = 3
        
        # bend speed
        self.bend_movement: float = 1.0
        
        # movement delta
        self.dx: float = 0.0
        self.dy: float = 0.0
        
        # capture size
        self.capture_size_set: bool = False
        self.width: float = 0.0
        self.height: float = 0.0
        
        # window size
        root = tkinter.Tk()
        self.screen_x: float = root.winfo_screenwidth()
        self.screen_y: float = root.winfo_screenheight()
    
    def close(self) -> None:
        return
    
    def set_capture_size(self, width, height) -> None:
        self.capture_size_set = True
        self.width = width
        self.height = height
    
    def update_landmarks(self, landmarks: list[tuple[float, float]]) -> None:
        self.landmarks = landmarks
        
        if not landmarks:
            self.pos = None
            return
        
        # palm points
        self.p1 = landmarks[0]
        self.p2 = landmarks[5]
        self.p3 = landmarks[17]
        
        # calculate new position (avg point)
        self.pos = ((self.p1[0] + self.p2[0] + self.p3[0]) / 3, (self.p1[1] + self.p2[1] + self.p3[1]) / 3)
        
        # fingertips
        self.f1 = landmarks[4]
        self.f2 = landmarks[8]
        self.f3 = landmarks[12]
        self.f4 = landmarks[16]
        self.f5 = landmarks[20]
        
        # check if fingers are bent
        self.threshold = get_dist(self.pos, [self.p1[0], self.p1[1]])
        
        threshold_weights = [
            0.75,
            1.0,
            1.0,
            1.0,
            1.0,
        ]
        
        self.f1_bend_dist = get_dist(self.pos, [self.f1[0], self.f1[1]]) / self.threshold
        self.f2_bend_dist = get_dist(self.pos, [self.f2[0], self.f2[1]]) / self.threshold
        self.f3_bend_dist = get_dist(self.pos, [self.f3[0], self.f3[1]]) / self.threshold
        self.f4_bend_dist = get_dist(self.pos, [self.f4[0], self.f4[1]]) / self.threshold
        self.f5_bend_dist = get_dist(self.pos, [self.f5[0], self.f5[1]]) / self.threshold
        
        self.f1_bent = self.f1_bend_dist < threshold_weights[0]
        self.f2_bent = self.f2_bend_dist < threshold_weights[1]
        self.f3_bent = self.f3_bend_dist < threshold_weights[2]
        self.f4_bent = self.f4_bend_dist < threshold_weights[3]
        self.f5_bent = self.f5_bend_dist < threshold_weights[4]
        
        self.interpret_landmarks()
    
    def interpret_landmarks(self) -> None:
        self.update_delta()
    
    def update_delta(self) -> None:
        dx, dy = self.get_position_change(self.pos)
        
        # update point deltas
        delta_p1 = get_dist([self.p1[0], self.p1[1]], [self.last_p1[0], self.last_p1[1]]) / self.threshold
        delta_p2 = get_dist([self.p2[0], self.p2[1]], [self.last_p2[0], self.last_p2[1]]) / self.threshold
        delta_p3 = get_dist([self.p3[0], self.p3[1]], [self.last_p3[0], self.last_p3[1]]) / self.threshold
        
        # anchor points
        points: int = 0
        
        if delta_p1 >= self.anchor_movement:
            points += 1
        if delta_p2 >= self.anchor_movement:
            points += 1
        if delta_p3 >= self.anchor_movement:
            points += 1
        
        if points < self.anchor_points:
            dx = 0.0
            dy = 0.0
        
        # finger bending
        delta_f1 = self.f1_bend_dist - self.last_f1
        
        if delta_f1 > self.bend_movement:
            dx = 0.0
            dy = 0.0
        
        self.last_f1 = self.f1_bend_dist
        
        # update position deltas
        self.dx = dx
        self.dy = dy
        
        # update last positions
        self.last_pos = (
            self.pos[0] if dx != 0 else self.last_pos[0],
            self.pos[1] if dy != 0 else self.last_pos[1]
        )
        
        if points >= self.anchor_points:
            self.last_p1 = self.p1
            self.last_p2 = self.p2
            self.last_p3 = self.p3
    
    def get_position_change(self, position: tuple[float, float]) -> tuple[float, float]:
        if not self.last_pos:
            self.last_pos = self.pos
            self.last_p1 = self.p1
            self.last_p2 = self.p2
            self.last_p3 = self.p3
            self.last_f1 = self.f1_bend_dist
            
            return (0, 0)
        
        # calculate deltas
        dx = -(position[0] - self.last_pos[0])
        dy = position[1] - self.last_pos[1]
        
        # convert from screen to 'threshold' space
        dx /= self.threshold
        dy /= self.threshold
        
        return (dx, dy)
    
    def test_bent(self, b1: BendState, b2: BendState, b3: BendState, b4: BendState, b5: BendState) -> bool:
        return (
            (int(b1) == int(self.f1_bent) or b1 == BendState.IGNORE) and
            (int(b2) == int(self.f2_bent) or b2 == BendState.IGNORE) and
            (int(b3) == int(self.f3_bent) or b3 == BendState.IGNORE) and
            (int(b4) == int(self.f4_bent) or b4 == BendState.IGNORE) and
            (int(b5) == int(self.f5_bent) or b5 == BendState.IGNORE)
        )
    
    def draw_hand(self, image) -> cv2.typing.MatLike:
        if not self.landmarks:
            return image
        
        # palm points
        image = draw_circle(image, self.p1[0], self.p1[1], (255, 0, 0))
        image = draw_circle(image, self.p2[0], self.p2[1], (255, 0, 0))
        image = draw_circle(image, self.p3[0], self.p3[1], (255, 0, 0))
        
        # center point
        if self.pos:
            image = draw_circle(image, self.pos[0], self.pos[1], (255, 0, 255))
        
        # finger tips
        image = draw_circle(image, self.f1[0], self.f1[1], (0, 0, 255) if self.f1_bent else (0, 255, 0))
        image = draw_circle(image, self.f2[0], self.f2[1], (0, 0, 255) if self.f2_bent else (0, 255, 0))
        image = draw_circle(image, self.f3[0], self.f3[1], (0, 0, 255) if self.f3_bent else (0, 255, 0))
        image = draw_circle(image, self.f4[0], self.f4[1], (0, 0, 255) if self.f4_bent else (0, 255, 0))
        image = draw_circle(image, self.f5[0], self.f5[1], (0, 0, 255) if self.f5_bent else (0, 255, 0))
        
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
                self.left_hand.update_landmarks([(point.x, point.y) for point in results.hand_landmarks[i]])
                l_updated = True
            elif handedness.category_name == 'Right':
                self.right_hand.update_landmarks([(point.x, point.y) for point in results.hand_landmarks[i]])
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

    def close(self) -> None:
        if self.left_hand:
            self.left_hand.close()
        if self.right_hand:
            self.right_hand.close()
    
    def set_capture_size(self, width, height) -> None:
        if self.left_hand:
            self.left_hand.set_capture_size(width, height)
        if self.right_hand:
            self.right_hand.set_capture_size(width, height)