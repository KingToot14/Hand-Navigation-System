import os
import multiprocessing as mp

from configparser import ConfigParser
import webview

from hand_nav.util import main_config
from hand_nav.nav_system import StandardNavSystem
from hand_nav.gamepad_system import GamepadSystem

class NavProcess:
    def __init__(self):
        self.process: mp.Process = None
        self.nav_system = None
    
    def start_thread(self, system):
        try:
            self.nav_system = system()
            self.nav_system.start()
        finally:
            self.nav_system.close()

class Api:
    def __init__(self):
        self.nav_system = None
        self.nav_process: mp.Process = None
        
        self.config: ConfigParser = main_config()
        
        self.window: webview.Window = None
        self.dummy: webview.Window = None
    
    def load_window(self):
        self.window = webview.active_window()
        
        return {
            'message': 'ok'
        }
    
    # --- Navigation --- #
    def start_thread(self, system):
        try:
            self.nav_system = system()
            self.nav_system.start()
        finally:
            self.nav_system.close()
    
    def create_dummy(self):
        print("Creating dummy:", self.window)
        
        if not self.window:
            return
        
        # prevents Windows from throttling
        self.dummy = webview.create_window('Dummy', html='', width=10, height=10, x=-200, y=0,
                                      on_top=True, resizable=False, frameless=True, shadow=False)
        
        self.window.events.closed += self.dummy.destroy
        
        return {
            'message': 'ok'
        }
    
    def destroy_dummy(self):
        if not self.dummy:
            return
        
        self.dummy.destroy()
        
        # remove old event
        if self.window:
            self.window.events.closed -= self.dummy.destroy
        
        self.dummy = None
        
        return {
            'message': 'ok'
        }
    
    def start_navigation(self, system: str):
        self.close_navigation()
        
        # start dummy
        if self.config.get('window', 'use_dummy') == 'True':
            self.create_dummy()
        
        # start process
        process = NavProcess()
        
        if system == 'standard':
            self.nav_process = mp.Process(target=process.start_thread, args=(StandardNavSystem,))
        elif system == 'gamepad':
            self.nav_process = mp.Process(target=process.start_thread, args=(GamepadSystem,))
        
        self.nav_process.start()
        self.nav_process.join()
        
        return {
            'message': 'ok'
        }
    
    def close_navigation(self):
        # clear old dummy
        if self.config.get('window', 'use_dummy') == 'True':
            self.destroy_dummy()
        
        if self.nav_process != None:
            # terminate process
            self.nav_process.terminate()
            self.nav_process.join()
            self.nav_process.close()
            
            self.nav_process = None
    
    
    # --- Config --- #
    def get_config(self, section, option):
        if not self.config:
            return {
                'message': '[err] Config not loaded'
            }
        
        return {
            'message': str(self.config.get(section, option))
        }
    
    def set_config(self, section, option, value):
        if not self.config:            
            return {
                'message': '[err] Config not loaded'
            }
        
        self.config.set(section, option, value)
        
        with open('config/config.ini', 'w') as file:
            self.config.write(file)
        
        return {
            'message': 'Set successfully'
        }