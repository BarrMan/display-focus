-- scripts/switch.applescript
on run argv
    set direction to item 1 of argv

    use framework "Foundation"
    use framework "AppKit"
    use framework "CoreGraphics"

    -- Get all screens
    set screens to current application's NSScreen's screens()

    -- Get window list
    set windowList to current application's CGWindowListCopyWindowInfo((current application's kCGWindowListOptionOnScreenOnly), 0)

    -- Find active window
    repeat with windowInfo in windowList
        set owner to windowInfo's objectForKey:"kCGWindowOwnerName" as text
        set alpha to windowInfo's objectForKey:"kCGWindowAlpha" as number
        
        if alpha is 1 and owner is not "Dock" and owner is not "Window Server" then
            -- Found active window, get its position
            set bounds to windowInfo's objectForKey:"kCGWindowBounds"
            set windowX to bounds's objectForKey:"X" as number
            set windowY to bounds's objectForKey:"Y" as number
            
            -- Find which display it's on
            repeat with i from 1 to count of screens
                set screen to item i of screens
                set frame to screen's frame()
                set screenX to frame's origin's x as number
                set screenY to frame's origin's y as number
                set screenW to frame's |size|'s width as number
                set screenH to frame's |size|'s height as number
                
                if windowX ≥ screenX and windowX < (screenX + screenW) then
                    -- Found the display, now get the target display
                    set targetIndex to i
                    
                    if direction is "left" and i > 1 then
                        set targetIndex to i - 1
                    else if direction is "right" and i < (count of screens) then
                        set targetIndex to i + 1
                    end if
                    
                    if targetIndex ≠ i then
                        set targetDisplay to item targetIndex of screens
                        
                        -- Find a window on the target display
                        repeat with targetWindow in windowList
                            set targetOwner to targetWindow's objectForKey:"kCGWindowOwnerName" as text
                            if targetOwner is not "Dock" and targetOwner is not "Window Server" then
                                set targetBounds to targetWindow's objectForKey:"kCGWindowBounds"
                                set targetX to targetBounds's objectForKey:"X" as number
                                
                                if targetX ≥ targetDisplay's frame()'s origin's x as number and ¬
                                    targetX < (targetDisplay's frame()'s origin's x as number + targetDisplay's frame()'s |size|'s width as number) then
                                    -- Found a window on target display, activate its application
                                    set pid to targetWindow's objectForKey:"kCGWindowOwnerPID"
                                    tell application "System Events"
                                        set processName to name of first process whose unix id is pid
                                        tell application processName to activate
                                    end tell
                                    return
                                end if
                            end if
                        end repeat
                    end if
                end if
            end repeat
        end if
    end repeat
end run