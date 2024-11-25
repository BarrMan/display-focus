import AppKit
from Quartz import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOptionOnScreenOnly


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
    return app_windows


def get_display_of_window(window, displays):
    """Determine which display a window is on."""
    if not window:
        return None

    bounds = window.get("kCGWindowBounds", {})
    x, y = bounds.get("X", 0), bounds.get("Y", 0)
    width, height = bounds.get("Width", 0), bounds.get("Height", 0)

    owner = window.get("kCGWindowOwnerName", "Unknown")
    title = window.get("kCGWindowName", "No Title")

    print(f"Checking Window: {owner} ('{title}') | Bounds: {bounds}")

    for i, display in enumerate(displays):
        frame = display.frame()
        # Adjust y-coordinate relative to the primary display
        adjusted_y = y - displays[0].frame().size.height if i > 0 else y
        print(f"  Comparing to Display {i + 1}: {frame} | Adjusted Y: {adjusted_y}")

        # Correctly calculate overlap
        x_overlap = frame.origin.x <= x + width and x <= frame.origin.x + frame.size.width
        y_overlap = frame.origin.y <= adjusted_y + height and adjusted_y <= frame.origin.y + frame.size.height

        if x_overlap and y_overlap:
            print(f"  -> Window '{owner}' ('{title}') matches Display {i + 1}")
            return i

    print(f"  -> Window '{owner}' ('{title}') does not match any display.")
    return None



def group_windows_by_display(displays, windows):
    """Group windows by the display they belong to."""
    grouped = {i: [] for i in range(len(displays))}

    for window in windows:
        display_index = get_display_of_window(window, displays)
        if display_index is not None:
            owner = window.get("kCGWindowOwnerName", "Unknown")
            title = window.get("kCGWindowName", "No Title")
            grouped[display_index].append(f"{owner} ('{title}')")

    return grouped


def main():
    """Main function to group and display windows by display."""
    displays = get_displays()
    windows = get_windows()

    grouped = group_windows_by_display(displays, windows)

    print("\nWindows grouped by display:")
    for i, display in grouped.items():
        print(f"Display {i + 1}: {display}")


if __name__ == "__main__":
    main()
