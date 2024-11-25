import sys
import os
from typing import Optional, Dict, Set
import time
from Quartz import (
    CGEventTapCreate,
    kCGEventKeyDown,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
    kCGHIDEventTap,  # Changed from kCGSessionEventTap
    kCGHeadInsertEventTap,
    CGEventGetFlags,
    CGEventGetIntegerValueField,
    kCGKeyboardEventKeycode,
    CGEventTapEnable,
    CFMachPortCreateRunLoopSource,
    CFRunLoopGetCurrent,
    CFRunLoopAddSource,
    kCFRunLoopCommonModes,
    CFRunLoopRun
)

# Key codes
LEFT_ARROW = 123
RIGHT_ARROW = 124

class GlobalHotkeyMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.tap = None
        self.runloop_source = None
        
    def handle_event(self, proxy, type_, event, refcon):
        """Handle keyboard events."""
        if type_ == kCGEventKeyDown:
            # Get keycode and flags
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            flags = CGEventGetFlags(event)
            
            # Check if Control and Shift are pressed
            is_ctrl = bool(flags & kCGEventFlagMaskControl)
            is_shift = bool(flags & kCGEventFlagMaskShift)
            
            if is_ctrl and is_shift:
                if keycode == LEFT_ARROW:
                    print("Ctrl+Shift+Left detected")
                    self.callback("left")
                    return None  # Consume the event
                elif keycode == RIGHT_ARROW:
                    print("Ctrl+Shift+Right detected")
                    self.callback("right")
                    return None  # Consume the event
        
        return event
    
    def start(self):
        """Start listening for keyboard events."""
        # Create a tap for keyboard events
        self.tap = CGEventTapCreate(
            kCGHIDEventTap,  # Changed to HID level for higher priority
            kCGHeadInsertEventTap,  # Insert at start of event chain
            0,  # Changed to 0 for more permissive filtering
            1 << kCGEventKeyDown,  # Only capture keydown events
            self.handle_event,
            None
        )
        
        if self.tap is None:
            print("Failed to create event tap. Make sure you have accessibility permissions enabled.")
            sys.exit(1)
        
        # Create a runloop source and add it to the current runloop
        self.runloop_source = CFMachPortCreateRunLoopSource(None, self.tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), self.runloop_source, kCFRunLoopCommonModes)
        
        # Enable the tap
        CGEventTapEnable(self.tap, True)
        
        print("Listening for global keyboard shortcuts...")
        print("Press Ctrl+Shift+Left/Right to switch displays")
        print("(Use Ctrl+C in the terminal to exit)")
        
        try:
            # Run the event loop
            CFRunLoopRun()
        except KeyboardInterrupt:
            print("\nShutting down...")