export const switchScript = `
use framework "Foundation"
use framework "AppKit"
use framework "CoreGraphics"

on run argv
    try
        if (count of argv) is 0 then
            error "Direction argument required"
        end if
        
        set direction to item 1 of argv
        
        -- Get screens using NSArray methods
        set screens to current application's NSScreen's screens()
        if screens is missing value then
            error "Could not get screen information"
        end if
        
        set screenCount to (screens's |count|()) as integer
        if screenCount < 1 then
            error "No screens detected"
        end if
        
        -- Get window list with error checking
        set windowList to current application's CGWindowListCopyWindowInfo((current application's kCGWindowListOptionOnScreenOnly), 0)
        if windowList is missing value then
            error "Could not get window list"
        end if
        
        set windowCount to (windowList's |count|()) as integer
        
        -- Find active window
        repeat with i from 0 to (windowCount - 1)
            try
                set windowInfo to windowList's objectAtIndex:i
                if windowInfo is missing value then
                    continue
                end if
                
                set owner to (windowInfo's objectForKey:"kCGWindowOwnerName") as text
                set alpha to (windowInfo's objectForKey:"kCGWindowAlpha" as number)
                
                if alpha is 1 and owner is not "Dock" and owner is not "Window Server" then
                    -- Found active window, get its position
                    set bounds to (windowInfo's objectForKey:"kCGWindowBounds")
                    if bounds is missing value then
                        continue
                    end if
                    
                    set windowX to (bounds's objectForKey:"X" as number)
                    set windowY to (bounds's objectForKey:"Y" as number)
                    
                    -- Find which display it's on
                    repeat with j from 0 to (screenCount - 1)
                        set screen to screens's objectAtIndex:j
                        set frame to screen's frame()
                        set screenX to (frame's origin's x as number)
                        set screenY to (frame's origin's y as number)
                        set screenW to (frame's |size|'s width as number)
                        set screenH to (frame's |size|'s height as number)
                        
                        if windowX ≥ screenX and windowX < (screenX + screenW) then
                            -- Found the display, now get the target display
                            set currentIndex to j
                            set targetIndex to currentIndex
                            
                            if direction is "left" and currentIndex > 0 then
                                set targetIndex to currentIndex - 1
                            else if direction is "right" and currentIndex < (screenCount - 1) then
                                set targetIndex to currentIndex + 1
                            end if
                            
                            if targetIndex ≠ currentIndex then
                                set targetDisplay to screens's objectAtIndex:targetIndex
                                
                                -- Find a window on the target display
                                repeat with k from 0 to (windowCount - 1)
                                    try
                                        set targetWindow to windowList's objectAtIndex:k
                                        if targetWindow is missing value then
                                            continue
                                        end if
                                        
                                        set targetOwner to (targetWindow's objectForKey:"kCGWindowOwnerName") as text
                                        if targetOwner is not "Dock" and targetOwner is not "Window Server" then
                                            set targetBounds to (targetWindow's objectForKey:"kCGWindowBounds")
                                            if targetBounds is missing value then
                                                continue
                                            end if
                                            
                                            set targetX to (targetBounds's objectForKey:"X" as number)
                                            
                                            set targetFrame to targetDisplay's frame()
                                            set targetScreenX to (targetFrame's origin's x as number)
                                            set targetScreenW to (targetFrame's |size|'s width as number)
                                            
                                            if targetX ≥ targetScreenX and targetX < (targetScreenX + targetScreenW) then
                                                -- Found a window on target display, activate its application
                                                set pid to targetWindow's objectForKey:"kCGWindowOwnerPID"
                                                tell application "System Events"
                                                    set processName to name of first process whose unix id is pid
                                                    tell application processName to activate
                                                end tell
                                                return
                                            end if
                                        end if
                                    on error windowError
                                        -- Skip problematic windows
                                        continue
                                    end try
                                end repeat
                            end if
                        end if
                    end repeat
                end if
            on error windowError
                -- Skip problematic windows
                continue
            end try
        end repeat
        
        -- If we get here, we couldn't find a window to switch to
        error "No suitable window found on target display"
        
    on error errMsg
        -- Return a proper error message
        error "Display switcher error: " & errMsg
    end try
end run`