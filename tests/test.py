from hand_nav.camera_manager import CameraManager
from hand_nav.hands import HandPair, Hand
from hand_nav.nav_system import HandPointer

if __name__ == "__main__":
    cam_manager = CameraManager(
        show_capture=True,
        pair=HandPair(
            Hand(),
            HandPointer()
        )
    )
    
    cam_manager.start_capture()