import math
import os

from configparser import ConfigParser

import cv2

def draw_circle(image, x: int, y: int, fill: tuple[float], outline: tuple[float] = (0, 0, 0), size: int = 5):
    height, width, _ = image.shape
    
    image = cv2.circle(image, (int(width * x), int(height * y)), size + 2, outline, -1)
    image = cv2.circle(image, (int(width * x), int(height * y)), size    , fill   , -1)
    
    return image

def get_sqr_dist(p1: tuple[float], p2: tuple[float]) -> float:
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

def get_dist(p1: tuple[float], p2: tuple[float]) -> float:
    return math.sqrt(get_sqr_dist(p1, p2))

def gamepad_default_config():
        config = ConfigParser()
        
        config['bindings'] = {
            'a_button':         'Right Thumb',
            'b_button':         'Right Pointer',
            'x_button':         'Right Ring',
            'y_button':         'Right Pinky',
            'dpad_up':          'Left Thumb',
            'dpad_down':        'Left Pointer',
            'dpad_left':        'Left Ring',
            'dpad_right':       'Left Pinky',
            'start':            'Unbound',
            'back':             'Unbound',
            'l_shoulder':       'Unbound',
            'r_shoulder':       'Unbound',
            'l_stick_up':       'Left Up Movement',
            'l_stick_down':     'Left Down Movement',
            'l_stick_left':     'Left Left Movement',
            'l_stick_right':    'Left Right Movement',
            'l_stick_press':    'Right Up Movement',
            'r_stick_up':       'Right Down Movement',
            'r_stick_down':     'Right Left Movement',
            'r_stick_left':     'Right Right Movement',
            'r_stick_right':    'Unbound',
            'r_stick_press':    'Unbound',
            'l_trigger':        'Unbound',
            'r_trigger':        'Unbound',
        }
        
        return config

def gamepad_config():
        config: ConfigParser
        
        if not os.path.exists('config/gamepad.ini'):
            config = gamepad_default_config()
        else:
            config = ConfigParser()
            config.read('config/gamepad.ini')
        
        return config