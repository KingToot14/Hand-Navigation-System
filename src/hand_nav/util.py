import cv2

def draw_circle(image, x: int, y: int, fill: tuple[int], outline: tuple[int] = (0, 0, 0), size: int = 5):
    height, width, _ = image.shape
    
    image = cv2.circle(image, (int(width * x), int(height * y)), size + 2, outline, -1)
    image = cv2.circle(image, (int(width * x), int(height * y)), size    , fill   , -1)
    
    return image