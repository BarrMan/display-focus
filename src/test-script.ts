export const switchScript = `
on run argv
    set direction to item 1 of argv
    log "Starting script with direction: " & direction
    
    tell application "System Events"
        -- First find the active window looking at window alpha
        set activeWindow to missing value
        set activeProcess to missing value
        
        repeat with currentProcess in (every process whose visible is true)
            try
                -- Skip Dock and Window Server
                set processName to name of currentProcess
                if processName is not "Dock" and processName is not "Window Server" then
                    repeat with currentWindow in (every window of currentProcess)
                        try
                            if value of attribute "AXFocused" of currentWindow is true then
                                set activeWindow to currentWindow
                                set activeProcess to currentProcess
                                exit repeat
                            end if
                        end try
                    end repeat
                end if
                if activeWindow is not missing value then
                    exit repeat
                end if
            end try
        end repeat
        
        if activeWindow is missing value then
            log "No active window found"
            return "No active window found"
        end if
        
        -- Get active window position and info
        set {activeX, activeY} to position of activeWindow
        set activeProcessName to name of activeProcess
        log "Active window: " & activeProcessName & " at {" & activeX & ", " & activeY & "}"
        
        -- Estimate display width based on screen resolution
        set displayWidth to 1920 -- This is an estimate, adjust if needed
        set currentDisplay to (activeX div displayWidth) + 1
        log "Current display: " & currentDisplay
        
        -- Calculate target display boundaries
        if direction is "right" then
            set targetDisplayStart to currentDisplay * displayWidth
            log "Looking for windows at x ≥ " & targetDisplayStart
        else
            set targetDisplayStart to (currentDisplay - 2) * displayWidth
            log "Looking for windows at x ≥ " & targetDisplayStart & " and x < " & activeX
        end if
        
        -- Find candidate window
        set candidateProcess to missing value
        set candidateWindow to missing value
        set bestDistance to 99999
        
        -- Look for windows in the target display
        repeat with currentProcess in (every process whose visible is true)
            try
                set processName to name of currentProcess
                if processName is not "Dock" and processName is not "Window Server" and processName is not activeProcessName then
                    repeat with currentWindow in (every window of currentProcess)
                        try
                            set {currentX, currentY} to position of currentWindow
                            set currentDisplay to (currentX div displayWidth) + 1
                            
                            if direction is "right" then
                                if currentX ≥ targetDisplayStart and currentDisplay > currentDisplay then
                                    set distance to currentX - activeX
                                    if distance < bestDistance then
                                        set candidateProcess to currentProcess
                                        set candidateWindow to currentWindow
                                        set bestDistance to distance
                                        log "Found candidate: " & processName & " at x=" & currentX & " (display " & currentDisplay & ")"
                                    end if
                                end if
                            else
                                if currentX ≥ targetDisplayStart and currentX < activeX and currentDisplay < currentDisplay then
                                    set distance to activeX - currentX
                                    if distance < bestDistance then
                                        set candidateProcess to currentProcess
                                        set candidateWindow to currentWindow
                                        set bestDistance to distance
                                        log "Found candidate: " & processName & " at x=" & currentX & " (display " & currentDisplay & ")"
                                    end if
                                end if
                            end if
                        end try
                    end repeat
                end if
            end try
        end repeat
        
        -- Switch to candidate window if found
        if candidateProcess is not missing value then
            set targetProcessName to name of candidateProcess
            log "Switching to: " & targetProcessName
            
            tell application targetProcessName to activate
            delay 0.1 -- Small delay to let activation complete
            
            tell candidateProcess
                set frontmost to true
                tell candidateWindow
                    perform action "AXRaise"
                    set focused to true
                end tell
            end tell
            
            return "Switched to " & targetProcessName
        end if
    end tell
    
    log "No suitable window found"
    return "No suitable window found"
end run`