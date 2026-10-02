#!/usr/bin/env bash

set -e

## Load helpers
source ./scripts/utils/macos-functions.sh > /dev/null

## Keyboard

# settings based on https://mac-key-repeat.zaymon.dev/
execute "defaults write NSGlobalDomain KeyRepeat -int 1" "Keyboard: Set 15 ms key repeat"
execute "defaults write NSGlobalDomain InitialKeyRepeat -int 13" "Keyboard: Set 195 ms initial delay"

## Files
execute "defaults write NSGlobalDomain AppleShowAllExtensions -bool true" "Show all filename extensions"

## Toolbar
showBatteryPercentage

## Dock
execute "defaults write com.apple.dock autohide -bool true" "Automatically hide and show the Dock"
execute "defaults write com.apple.dock autohide-delay -float 0" "Remove the auto-hiding Dock delay"
execute "defaults write com.apple.dock autohide-time-modifier -float 0" "Remove the animation when hiding/showing the Dock"
execute "defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false" "Keyboard: Disable tooltip when holding key"
execute "defaults write com.apple.dock show-recents -bool false" "Don't show recent applications in Dock"
execute "defaults write com.apple.dock show-process-indicators -bool false" "Don't show indicator for running Apps"

# Clear dock
execute "defaults write com.apple.dock persistent-apps -array" "Remove all persistent apps from dock"

# Clear dock - downloads, etc.
execute "defaults write com.apple.dock persistent-others -array" "Remove all persistent others from dock"

# Add my apps in order to dock
addAppToDock "Launchpad"
addAppToDock "Firefox"
addAppToDock "Slack"
addAppToDock "Ghostty"
addAppToDock "Visual Studio Code"
addAppToDock "Obsidian"
addAppToDock "Spotify"
addAppToDock "Claude"

# Dock size and position
defaults write com.apple.dock tilesize -int 48
defaults write com.apple.dock orientation -string "right"

# See changes
restartDock

# Todo - for aerospace
# https://nikitabobko.github.io/AeroSpace/guide#a-note-on-displays-have-separate-spaces
# defaults write com.apple.spaces spans-displays -bool true && killall SystemUIServer
