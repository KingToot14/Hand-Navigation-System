import time

from pynput.keyboard import Key, Controller as KeyController, Listener as KeyListener
from pynput.mouse import Controller as MouseController, Listener as MouseListener

def _on_press(key, injected) -> None:
    try:
        print(f"key: {key.char} (injected: {injected})")
    except AttributeError:
        print(f"special key: {key} (injected: {injected})")

if __name__ == "__main__":
    # keyboard testing
    listener = KeyListener(on_press=_on_press)
    
    listener.start()
    
    keyboard = KeyController()
    
    keyboard.press(Key.space)
    keyboard.release(Key.space)
    
    # mouse testing
    mouse = MouseController()
    
    time.sleep(1)
    mouse.position = (100, 100)
    
    time.sleep(1)
    mouse.position = (100, 700)
    
    time.sleep(1)
    mouse.position = (700, 700)
    
    time.sleep(1) 
    mouse.position = (700, 100) 

    
    