import sys
import os
from typing import Optional
import subprocess
import platform
import time
from pynput import keyboard
from ApplicationServices import AXIsProcessTrusted

class AccessibilityPermissionHandler:
    """Handles macOS accessibility permissions for input monitoring."""
    
    @staticmethod
    def is_macos() -> bool:
        """Check if the current system is macOS."""
        return sys.platform == 'darwin'
    
    @staticmethod
    def check_permissions_external():
        """Check permissions using a separate Python process."""
        script = '''
import sys
from ApplicationServices import AXIsProcessTrusted
sys.exit(0 if AXIsProcessTrusted() else 1)
        '''
        
        result = subprocess.run(
            [sys.executable, '-c', script],
            capture_output=True
        )
        return result.returncode == 0
    
    @staticmethod
    def open_privacy_settings():
        """Open the Security & Privacy system preferences panel."""
        subprocess.Popen(['open', 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'])
    
    @staticmethod
    def request_permissions():
        """Request accessibility permissions with a native dialog."""
        if not AccessibilityPermissionHandler.is_macos():
            return True

        script = '''
            tell application "System Events"
                activate
                set theAlertText to "This app requires accessibility permissions to detect keyboard shortcuts. Would you like to open System Settings to grant permission?"
                display dialog theAlertText buttons {"Cancel", "Open Settings"} default button 2 with title "Accessibility Permissions Required"
                if button returned of result is "Open Settings" then
                    return true
                else
                    return false
                end if
            end tell
        '''
        
        try:
            p = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE)
            result = p.communicate()[0].strip()
            if result == b'true':
                AccessibilityPermissionHandler.open_privacy_settings()
                print("\nWaiting for permissions to be granted...")
                return True
            return False
        except:
            # Fallback to simple subprocess call if AppleScript fails
            response = input("\nWould you like to open System Settings to grant permission? (y/n): ")
            if response.lower() == 'y':
                AccessibilityPermissionHandler.open_privacy_settings()
                return True
            return False

def wait_for_accessibility_permissions():
    """Wait for the user to grant accessibility permissions."""
    handler = AccessibilityPermissionHandler()
    
    max_attempts = 3
    attempt = 0
    
    while not handler.check_permissions_external() and attempt < max_attempts:
        print("Checking accessibility permissions...")
        if handler.request_permissions():
            print("\nPlease grant accessibility permissions in System Settings:")
            print("1. Click the lock icon to make changes")
            print("2. Find and check the box next to Terminal (or your Python IDE)")
            print("3. Check the box and wait...")
            
            # Wait for permissions with timeout
            timeout = 60  # 60 seconds timeout
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                if handler.check_permissions_external():
                    print("\nPermissions granted! Starting the application...")
                    return True
                time.sleep(0.5)
                
            attempt += 1
            if attempt < max_attempts:
                print("\nPermission grant timed out. Trying again...")
        else:
            print("Accessibility permissions are required for this application to work.")
            sys.exit(1)
            
    if not handler.check_permissions_external():
        print("Failed to get accessibility permissions after several attempts.")
        sys.exit(1)
        
    return True