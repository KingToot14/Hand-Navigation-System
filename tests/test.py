from hand_nav.camera_manager import CameraManager

if __name__ == "__main__":
    cam_manager = CameraManager(
        show_capture=True
    )
    
    cam_manager.start_capture()