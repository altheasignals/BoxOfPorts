# BoxOfPorts GUI Operators Guide
*"For those who like their operations point-and-click smooth"*

## 🌹 Welcome to the Easy Way

Sometimes you just want to **keep on truckin'** without memorizing commands. This guide is for operators who prefer the mouse to the keyboard - no shame in that! Even Jerry Garcia used picks instead of fingers sometimes.

**For the Lazy Lightning crowd**: We'll set you up with desktop shortcuts, batch files, and double-click solutions that make SMS gateway management as easy as **riding that train**.

---

## 🎸 Desktop Shortcuts - Your Greatest Hits

### macOS Command Files

These magical `.command` files will open Terminal, run the operation, and show you the results. **What a long strange trip** it's been to get here!

#### 1. 📱 "Touch of Grey" - Quick SMS Test
```bash
# Save as: ~/Desktop/Touch_of_Grey_SMS_Test.command
#!/bin/bash
cd ~/BoxOfPorts
source venv/bin/activate

echo "🎵 Touch of Grey - Quick SMS Test 🎵"
echo "===================================="
echo ""
echo "Testing SMS functionality..."

# Get current profile
CURRENT_PROFILE=$(boxofports config current | head -n1 | cut -d':' -f2 | xargs)
if [ -z "$CURRENT_PROFILE" ] || [ "$CURRENT_PROFILE" = "No current profile set" ]; then
    echo "❌ No profile set. Please run 'Setup_Profiles.command' first."
else
    echo "Using profile: $CURRENT_PROFILE"
    echo ""
    echo "Sending test SMS..."
    boxofports sms send --to "+1234567890" --text "Touch of grey, BoxOfPorts test at $(date)" --ports "1A" --dry-run
fi

echo ""
echo "🌹 Touch of grey, will get you through! 🌹"
echo "Press any key to close..."
read -n 1
```

#### 2. 👁️ "Eyes of the World" - Inbox Monitor
```bash
# Save as: ~/Desktop/Eyes_of_the_World_Inbox.command
#!/bin/bash
cd ~/BoxOfPorts
source venv/bin/activate

echo "🎵 Eyes of the World - Inbox Monitor 🎵"
echo "========================================"
echo ""

# Export inbox with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DESKTOP_PATH="$HOME/Desktop"

echo "Wake up to find out that you are the eyes of the world..."
echo ""
echo "📥 Exporting SMS inbox..."
boxofports inbox list --count 50 --json > "${DESKTOP_PATH}/sms_inbox_${TIMESTAMP}.json"

echo "📊 Generating inbox summary..."
boxofports inbox summary > "${DESKTOP_PATH}/inbox_summary_${TIMESTAMP}.txt"

echo ""
echo "✅ Files saved to Desktop:"
echo "  📄 sms_inbox_${TIMESTAMP}.json"
echo "  📊 inbox_summary_${TIMESTAMP}.txt"
echo ""
echo "🌍 The eyes of the world are watching your messages! 🌍"
echo "Press any key to close..."
read -n 1
```

#### 3. ⚡ "Fire on the Mountain" - Emergency Alert
```bash
# Save as: ~/Desktop/Fire_on_the_Mountain_Alert.command
#!/bin/bash
cd ~/BoxOfPorts
source venv/bin/activate

echo "🎵 Fire on the Mountain - Emergency Alert 🎵"
echo "=============================================="
echo ""

# Get recipient number from user
echo "🔥 EMERGENCY ALERT SYSTEM 🔥"
echo ""
read -p "Enter recipient number (e.g. +1234567890): " RECIPIENT
read -p "Enter alert message: " MESSAGE

if [ -n "$RECIPIENT" ] && [ -n "$MESSAGE" ]; then
    echo ""
    echo "🚨 Sending emergency alert..."
    echo "Fire on the mountain, run boys run!"
    echo ""
    
    # Send via multiple ports for reliability
    boxofports sms spray --to "$RECIPIENT" --text "🚨 ALERT: $MESSAGE - Sent at $(date)" --ports "1A,2A,3A"
    
    echo ""
    echo "🔥 Emergency alert sent via multiple ports! 🔥"
else
    echo "❌ Alert cancelled - missing recipient or message"
fi

echo ""
echo "Press any key to close..."
read -n 1
```

#### 4. 🌊 "Ripple" - Bulk Campaign Launcher  
```bash
# Save as: ~/Desktop/Ripple_Bulk_Campaign.command
#!/bin/bash
cd ~/BoxOfPorts
source venv/bin/activate

echo "🎵 Ripple - Bulk Campaign Launcher 🎵"
echo "====================================="
echo ""

echo "Let it be known there is a fountain..."
echo "That ripples your messages to all the ports!"
echo ""

# Get campaign details
read -p "Enter recipient number: " RECIPIENT
read -p "Enter campaign message: " MESSAGE  
read -p "Enter port range (e.g. 1A-1D): " PORTS
read -p "How many times to repeat? (default: 1): " REPEAT

# Set defaults
REPEAT=${REPEAT:-1}

if [ -n "$RECIPIENT" ] && [ -n "$MESSAGE" ] && [ -n "$PORTS" ]; then
    echo ""
    echo "🌊 Launching ripple campaign..."
    echo "Reach out your hand if your cup be empty..."
    echo ""
    
    # Preview first
    echo "📋 Campaign Preview:"
    boxofports sms send --to "$RECIPIENT" --text "$MESSAGE from port {{port}} ({{idx}})" --ports "$PORTS" --repeat "$REPEAT" --dry-run
    
    echo ""
    read -p "Send this campaign? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🌊 Sending ripple campaign..."
        boxofports sms send --to "$RECIPIENT" --text "$MESSAGE from port {{port}} ({{idx}})" --ports "$PORTS" --repeat "$REPEAT"
        echo "✅ Ripple campaign complete!"
    else
        echo "📋 Campaign cancelled"
    fi
else
    echo "❌ Campaign cancelled - missing information"
fi

echo ""
echo "🌊 If you plant ice, you're gonna harvest wind! 🌊"
echo "Press any key to close..."
read -n 1
```

#### 5. 🌹 "Scarlet Begonias" - STOP Messages Report
```bash
# Save as: ~/Desktop/Scarlet_Begonias_STOP_Report.command
#!/bin/bash
cd ~/BoxOfPorts
source venv/bin/activate

echo "🎵 Scarlet Begonias - STOP Messages Report 🎵"
echo "==============================================="
echo ""

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DESKTOP_PATH="$HOME/Desktop"

echo "Once in a while you get shown the light..."
echo "In the strangest of places if you look at it right!"
echo ""
echo "🛑 Generating STOP messages compliance report..."

# Export STOP messages
boxofports inbox stop --json > "${DESKTOP_PATH}/stop_messages_${TIMESTAMP}.json"
boxofports inbox stop > "${DESKTOP_PATH}/stop_messages_readable_${TIMESTAMP}.txt"

# Count STOP messages
STOP_COUNT=$(boxofports inbox stop --json 2>/dev/null | jq length 2>/dev/null || echo "0")

echo ""
echo "📊 STOP Messages Analysis Complete:"
echo "  🛑 Total STOP messages: $STOP_COUNT"
echo "  📄 JSON report: stop_messages_${TIMESTAMP}.json"  
echo "  📝 Readable report: stop_messages_readable_${TIMESTAMP}.txt"
echo ""
echo "🌹 Well, I had to learn the hard way! 🌹"
echo "Press any key to close..."
read -n 1
```

#### 6. 🚂 "Casey Jones" - Gateway Status Check
```bash
# Save as: ~/Desktop/Casey_Jones_Status_Check.command
#!/bin/bash
cd ~/BoxOfPorts
source venv/bin/activate

echo "🎵 Casey Jones - Gateway Status Check 🎵"
echo "========================================"
echo ""

echo "Driving that train, high on... gateway connectivity!"
echo "Casey Jones you better watch your gateways!"
echo ""

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="$HOME/Desktop/gateway_status_${TIMESTAMP}.txt"

echo "🚂 Testing all configured gateways..." | tee "$RESULTS_FILE"
echo "====================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Test each profile
PROFILES=$(boxofports config list 2>/dev/null | tail -n +2 | awk '{print $1}' | grep -v '^$')

if [ -z "$PROFILES" ]; then
    echo "❌ No profiles configured! Casey's got no train to drive!" | tee -a "$RESULTS_FILE"
    echo "Run 'Setup_Profiles.command' first." | tee -a "$RESULTS_FILE"
else
    for profile in $PROFILES; do
        echo "🚂 Testing profile: $profile" | tee -a "$RESULTS_FILE"
        echo "────────────────────────────" >> "$RESULTS_FILE"
        
        if boxofports config switch "$profile" >> "$RESULTS_FILE" 2>&1; then
            if boxofports test-connection >> "$RESULTS_FILE" 2>&1; then
                echo "✅ $profile: Connection successful - Casey's on time!" | tee -a "$RESULTS_FILE"
            else
                echo "❌ $profile: Connection failed - Casey's trouble ahead!" | tee -a "$RESULTS_FILE"
            fi
        else
            echo "❌ $profile: Profile switch failed!" | tee -a "$RESULTS_FILE"
        fi
        echo "" >> "$RESULTS_FILE"
    done
fi

echo ""
echo "📊 Status report saved to: gateway_status_${TIMESTAMP}.txt"
echo ""
echo "🚂 Keep on driving that train! 🚂"
echo "Press any key to close..."
read -n 1
```

#### 7. 🔧 "Uncle John's Band" - Profile Setup Helper
```bash
# Save as: ~/Desktop/Uncle_Johns_Band_Setup.command
#!/bin/bash
cd ~/BoxOfPorts
source venv/bin/activate

echo "🎵 Uncle John's Band - Profile Setup Helper 🎵"
echo "==============================================="
echo ""

echo "Come hear Uncle John's band by the riverside!"
echo "Got some things to talk about, here beside the rising tide..."
echo ""
echo "🔧 Gateway Profile Setup Wizard"
echo ""

while true; do
    echo "What would you like to do?"
    echo "1. 📋 List existing profiles"
    echo "2. ➕ Add new profile"  
    echo "3. 🔄 Switch profile"
    echo "4. ❌ Remove profile"
    echo "5. 🚪 Exit"
    echo ""
    read -p "Choose your option (1-5): " choice
    
    case $choice in
        1)
            echo ""
            echo "📋 Your current profiles:"
            boxofports config list
            echo ""
            ;;
        2)
            echo ""
            echo "➕ Adding new gateway profile..."
            read -p "Profile name: " name
            read -p "Gateway IP (e.g. 192.168.1.100): " host
            read -p "Username (default: admin): " user
            read -s -p "Password: " password
            echo ""
            
            user=${user:-admin}
            
            if [ -n "$name" ] && [ -n "$host" ] && [ -n "$password" ]; then
                boxofports config add-profile "$name" --host "$host" --user "$user" --password "$password"
                echo "✅ Profile '$name' added successfully!"
            else
                echo "❌ Missing required information"
            fi
            echo ""
            ;;
        3)
            echo ""
            echo "🔄 Available profiles:"
            boxofports config list
            echo ""
            read -p "Switch to profile: " profile
            if [ -n "$profile" ]; then
                boxofports config switch "$profile"
            fi
            echo ""
            ;;
        4)
            echo ""
            echo "❌ Available profiles:"
            boxofports config list
            echo ""
            read -p "Remove profile: " profile
            if [ -n "$profile" ]; then
                read -p "Are you sure? (y/N): " -n 1 confirm
                echo ""
                if [[ $confirm =~ ^[Yy]$ ]]; then
                    boxofports config remove "$profile"
                fi
            fi
            echo ""
            ;;
        5)
            break
            ;;
        *)
            echo "❌ Invalid choice. Uncle John says try again!"
            echo ""
            ;;
    esac
done

echo ""
echo "🎸 Come back tomorrow, Uncle John's band will be here! 🎸"
echo "Press any key to close..."
read -n 1
```

---

### 🪟 Windows Batch Files

For our Windows **truckin'** friends, here are some batch files that'll make your day:

#### 1. 📱 Touch of Grey SMS Test
```batch
@echo off
REM Save as: Touch_of_Grey_SMS_Test.bat
cd /d "%USERPROFILE%\BoxOfPorts"
call venv\Scripts\activate.bat

echo.
echo   🎵 Touch of Grey - Quick SMS Test 🎵
echo   ====================================
echo.
echo   Testing SMS functionality...
echo.

python -m boxofports.cli config current
if errorlevel 1 (
    echo   ❌ No profile configured. Run Uncle_Johns_Band_Setup.bat first.
) else (
    echo   Sending test SMS...
    python -m boxofports.cli sms send --to "+1234567890" --text "Touch of grey, BoxOfPorts test" --ports "1A" --dry-run
)

echo.
echo   🌹 Touch of grey, will get you through! 🌹
pause
```

#### 2. 👁️ Eyes of the World Inbox
```batch
@echo off
REM Save as: Eyes_of_the_World_Inbox.bat
cd /d "%USERPROFILE%\BoxOfPorts"
call venv\Scripts\activate.bat

echo.
echo   🎵 Eyes of the World - Inbox Monitor 🎵
echo   ========================================
echo.

set TIMESTAMP=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo   Wake up to find out that you are the eyes of the world...
echo.
echo   📥 Exporting SMS inbox...
python -m boxofports.cli inbox list --count 50 --json > "%USERPROFILE%\Desktop\sms_inbox_%TIMESTAMP%.json"

echo   📊 Generating inbox summary...
python -m boxofports.cli inbox summary > "%USERPROFILE%\Desktop\inbox_summary_%TIMESTAMP%.txt"

echo.
echo   ✅ Files saved to Desktop:
echo     📄 sms_inbox_%TIMESTAMP%.json
echo     📊 inbox_summary_%TIMESTAMP%.txt
echo.
echo   🌍 The eyes of the world are watching your messages! 🌍
pause
```

#### 3. 🔥 Fire on the Mountain Alert
```batch
@echo off
REM Save as: Fire_on_the_Mountain_Alert.bat
cd /d "%USERPROFILE%\BoxOfPorts"
call venv\Scripts\activate.bat

echo.
echo   🎵 Fire on the Mountain - Emergency Alert 🎵
echo   ==============================================
echo.
echo   🔥 EMERGENCY ALERT SYSTEM 🔥
echo.

set /p RECIPIENT=Enter recipient number (e.g. +1234567890): 
set /p MESSAGE=Enter alert message: 

if "%RECIPIENT%" neq "" if "%MESSAGE%" neq "" (
    echo.
    echo   🚨 Sending emergency alert...
    echo   Fire on the mountain, run boys run!
    echo.
    python -m boxofports.cli sms spray --to "%RECIPIENT%" --text "🚨 ALERT: %MESSAGE%" --ports "1A,2A,3A"
    echo.
    echo   🔥 Emergency alert sent via multiple ports! 🔥
) else (
    echo   ❌ Alert cancelled - missing recipient or message
)

echo.
pause
```

---

## 🎯 Installation Instructions

### macOS Setup
```bash
# First, install BoxOfPorts normally, then:

# 1. Make desktop shortcuts directory
mkdir -p ~/Desktop/BoxOfPorts_Shortcuts

# 2. Copy all the .command files above to that folder
# 3. Make them all executable:
chmod +x ~/Desktop/BoxOfPorts_Shortcuts/*.command

# 4. Double-click to run!
```

### Windows Setup  
```batch
REM 1. Install BoxOfPorts normally, then:
REM 2. Create a folder on Desktop called "BoxOfPorts_Shortcuts"
REM 3. Save all the .bat files above in that folder
REM 4. Double-click to run!
```

---

## 🌈 Troubleshooting - "Trouble Ahead, Trouble Behind"

### Common Issues

**🎵 "What a long strange trip it's been..."**

- **Shortcut won't run**: Make sure BoxOfPorts is installed correctly first
- **"No profiles configured"**: Run the Uncle John's Band setup helper first  
- **Python command not found**: Your PATH isn't set up right - check the main installation guide

### Getting Help

**🎸 "I need a miracle every day!"**

When shortcuts don't work:
1. Open Terminal/Command Prompt manually
2. Navigate to your BoxOfPorts directory  
3. Run `boxofports --help` (macOS) or `python -m boxofports.cli --help` (Windows)
4. If that works, the shortcuts just need the paths fixed

---

## 🌹 Final Words

**"What I want to know, is are you kind?"**

These shortcuts are designed with **kindness** in mind - for operators who just want to get their work done without memorizing commands. There's **nothing wrong with point-and-click** operations!

Remember: Whether you're a command-line wizard or a GUI guru, we're all just **keeping on truckin'** in this wild world of SMS gateways.

**"Box of rain will wash away the weary"** - and these shortcuts will wash away the command-line complexity!

---

*🎵 "Sometimes the light's all shining on me, other times I can barely see" 🎵*

**Happy clicking!** 🖱️✨

---

**BoxOfPorts GUI Operators Guide**  
*For the Lazy Lightning crowd*  
Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.