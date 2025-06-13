import cv2

def draw_circle(image, x: int, y: int, fill: tuple[float], outline: tuple[float] = (0, 0, 0), size: int = 5):
    height, width, _ = image.shape
    
    image = cv2.circle(image, (int(width * x), int(height * y)), size + 2, outline, -1)
    image = cv2.circle(image, (int(width * x), int(height * y)), size    , fill   , -1)
    
    return image

def get_sqr_dist(p1: tuple[float], p2: tuple[float]) -> float:
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2