from hand_nav.app.api import Api

if __name__ == "__main__":
    api = Api()
    
    try:
        api.start_navigation('standard')
        # api.start_navigation('gamepad')
    finally:
        api.close_navigation()