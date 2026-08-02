
# Run a command and print a description
# - usage: execute "command" "description"
function execute() {
    echo "  -> $2"
    eval "$1"
}
export -f execute

# Add an Application to the macOS Dock
# - usage: addAppToDock "[Application Name]"
# - example: addAppToDock "Terminal"
# Source: https://github.com/rpavlick/add_to_dock
function addAppToDock() {
    local app_name="$1"
    local launchservices_path="/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister"
    local app_path=$($launchservices_path -dump | grep -o "/.*$app_name.app" | grep -v -E "Backups|Caches|TimeMachine|Temporary|/Volumes/$app_name" | uniq | sort | head -n1)
    if open -Ra "$app_path"; then
       defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>$app_path</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>"
    else
       echo "Warning: Application not found: $1" >&2
    fi
}
export -f addAppToDock

# --> Show % for Battery
function showBatteryPercentage(){
	# Show the Battery Icon in Menu Bar
	defaults write com.apple.controlcenter "NSStatusItem Visible Battery" -int 1
	# Show the Battery % Percentage in Menu Bar
	defaults write com.apple.controlcenter "BatteryShowPercentage" -bool TRUE
}
export -f showBatteryPercentage

# --> Restart the Dock process
function restartDock(){
    killall Dock
}
export -f restartDock

