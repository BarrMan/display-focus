#! .venv/bin/python

import sys
import AppKit
from Quartz import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOptionOnScreenOnly
# from pynput import keyboard

# from keyboard_handler import GlobalHotkeyMonitor
# import permissions_handler


def get_displays():
    """Retrieve all connected displays and their frames."""
    displays = AppKit.NSScreen.screens()
    print("\nDetected Displays:")
    for i, display in enumerate(displays):
        print(f"  Display {i + 1}: {display.frame()}")
    return displays


def get_windows():
    """Retrieve all visible windows, filtering out non-app elements."""
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    app_windows = [
        window for window in windows
        if window.get("kCGWindowLayer", 0) == 0  # Only application windows
    ]
    for window in app_windows:
        print(f"  {window.get('kCGWindowOwnerName')} - {window.get('kCGWindowName')}")
    return app_windows


def get_display_of_window(window, displays):
    """Determine which display a window is on."""
    if not window:
        return None

    bounds = window.get("kCGWindowBounds", {})
    x, y, width, height = (
        bounds.get("X", 0),
        bounds.get("Y", 0),
        bounds.get("Width", 0),
        bounds.get("Height", 0),
    )

    print(f"  {window.get('kCGWindowOwnerName')} - {window.get('kCGWindowName')}")
    
    for i, display in enumerate(displays):
        frame = display.frame()
        adjusted_y = y - displays[0].frame().size.height if i > 0 else y
        x_overlap = frame.origin.x <= x + width and x + width <= frame.origin.x + frame.size.width
        y_overlap = frame.origin.y <= adjusted_y + height and adjusted_y + height <= frame.origin.y + frame.size.height
        if x_overlap and y_overlap:
            return i, display
    return None


def find_topmost_window_on_display(target_display, target_index, displays):
    """Find the topmost window on the target display."""
    windows = get_windows()
    for window in windows:
        result = get_display_of_window(window, displays)
        print(f"  {window.get('kCGWindowOwnerName')} - {window.get('kCGWindowName')}")
        print(f"result: {result}")
        if result and result[1] == target_display:
            return window
    return None


def focus_window(window):
    """Bring a window to the foreground by activating its owning application."""
    if not window:
        return
    pid = window.get("kCGWindowOwnerPID")
    running_apps = AppKit.NSWorkspace.sharedWorkspace().runningApplications()
    for app in running_apps:
        if app.processIdentifier() == pid:
            app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            return
        
        
def switch_display(direction="right"):
    """
    Switch focus between displays based on the direction (left or right).
    """
    displays = get_displays()
    if len(displays) < 2:
        print("You need at least two displays connected.")
        return

    # Look through all windows to find the active one
    windows = get_windows()
    for window in windows:
        owner = window.get('kCGWindowOwnerName')
        name = window.get('kCGWindowName')
        status = window.get('kCGWindowAlpha', 0)
        print(f"Window: {owner} - {name} - Alpha: {status}")

        # The active window typically has an alpha of 1
        if status == 1 and owner not in ["Dock", "Window Server"]:
            active_window = window
            print(f"Found active window: {owner} - {name}")
            break
    else:
        print("No active window found")
        return

    active_result = get_display_of_window(active_window, displays)
    if not active_result:
        print("Could not determine the active display.")
        return
    active_index, active_display = active_result
    print(f"Active window is on display: {active_index + 1}")

    # Determine the target display
    if direction == "right":
        target_index = (active_index + 1) % len(displays)  # Wrap around
    elif direction == "left":
        target_index = (active_index - 1) % len(displays)  # Wrap around
    else:
        return

    target_display = displays[target_index]
    print(f"Targeting display: {target_index + 1}")

    # Find the topmost window on the target display
    target_window = find_topmost_window_on_display(target_display, target_index, displays)
    if target_window:
        print(f"\nSwitching from {active_window.get('kCGWindowOwnerName')} to {target_window.get('kCGWindowOwnerName')}")
        focus_window(target_window)
    else:
        print(f"No active windows found on Display {target_index + 1}.")

if __name__ == "__main__":
    # if permissions_handler.wait_for_accessibility_permissions():
    #     monitor = GlobalHotkeyMonitor(switch_display)
    #     monitor.start()

    switch_display(sys.argv[1])
