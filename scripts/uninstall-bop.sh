#!/usr/bin/env bash
# BoxOfPorts Uninstaller - "Sometimes the light's all shinin' on me"
# Detects and removes all forms of BoxOfPorts installations to avoid conflicts
# Safe for remote execution: curl -fsSL https://...uninstall-bop.sh | bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detection results
DETECTED_INSTALLATIONS=()
DETECTED_CONFIGS=()
DETECTED_DATA=()

print_header() {
    echo -e "${BLUE}"
    echo "BoxOfPorts Uninstaller"
    echo "Sometimes the light's all shinin' on me"
    echo "======================================="
    echo "Scanning for all installations to avoid version conflicts..."
    echo -e "${NC}"
}

print_section() {
    echo -e "\n${YELLOW}$1${NC}"
    echo "$(printf '%.0s-' {1..50})"
}

add_detection() {
    local type="$1"
    local path="$2" 
    local description="$3"
    local method="$4"
    
    case "$type" in
        "install")
            DETECTED_INSTALLATIONS+=("$path|$description|$method")
            ;;
        "config")
            DETECTED_CONFIGS+=("$path|$description|$method")
            ;;
        "data")
            DETECTED_DATA+=("$path|$description|$method")
            ;;
    esac
}

# Check for pip installations
check_pip_installations() {
    print_section "🔍 Checking pip installations..."
    
    # Global pip
    if pip show boxofports >/dev/null 2>&1; then
        local version=$(pip show boxofports | grep "Version:" | cut -d' ' -f2 || echo "unknown")
        local bop_path=$(which bop 2>/dev/null || echo 'pip global')
        add_detection "install" "$bop_path" "pip global install (v$version)" "pip_global"
        echo -e "  ${RED}✓${NC} Found pip global installation (version: $version)"
    fi
    
    # pip --user installations
    if pip show --user boxofports >/dev/null 2>&1; then
        local version=$(pip show --user boxofports | grep "Version:" | cut -d' ' -f2 || echo "unknown")
        add_detection "install" "$HOME/.local/bin/bop" "pip user install (v$version)" "pip_user"
        echo -e "  ${RED}✓${NC} Found pip --user installation (version: $version)"
    fi
}

# Check for conda/mamba installations (skip - not in our recommended install methods)
check_conda_installations() {
    print_section "🔍 Checking conda/mamba installations..."
    echo -e "  ${YELLOW}ℹ${NC} Skipping conda/mamba - not a recommended installation method"
}

# Check for Docker wrapper installations  
check_docker_wrapper() {
    print_section "🔍 Checking Docker wrapper installations..."
    
    # Common installation paths
    local wrapper_paths=(
        "/usr/local/bin/bop"
        "/usr/bin/bop" 
        "$HOME/.local/bin/bop"
        "$HOME/bin/bop"
        "./bop"
        "./scripts/bop"
    )
    
    for path in "${wrapper_paths[@]}"; do
        if [[ -f "$path" ]] && [[ -x "$path" ]]; then
            # Check if it's our Docker wrapper by looking for DOCKER_IMAGE variable
            if grep -q "DOCKER_IMAGE=" "$path" 2>/dev/null; then
                local image=$(grep "DOCKER_IMAGE=" "$path" | head -1 | cut -d'"' -f2)
                add_detection "install" "$path" "Docker wrapper (image: $image)" "docker_wrapper"
                echo -e "  ${RED}✓${NC} Found Docker wrapper: $path (image: $image)"
            fi
        fi
    done
    
    # Check PATH for any bop commands
    if command -v bop >/dev/null 2>&1; then
        local bop_path=$(which bop)
        if [[ "$bop_path" != *"/usr/local/bin/bop"* ]] && [[ "$bop_path" != *"/.local/bin/bop"* ]]; then
            # This might be a different installation
            if grep -q "DOCKER_IMAGE=" "$bop_path" 2>/dev/null; then
                local image=$(grep "DOCKER_IMAGE=" "$bop_path" | head -1 | cut -d'"' -f2 || echo "unknown")
                add_detection "install" "$bop_path" "Docker wrapper in PATH (image: $image)" "docker_wrapper"
                echo -e "  ${RED}✓${NC} Found Docker wrapper in PATH: $bop_path"
            else
                add_detection "install" "$bop_path" "Unknown bop installation" "unknown"
                echo -e "  ${RED}✓${NC} Found unknown bop installation: $bop_path"
            fi
        fi
    fi
}

# Check for development installations (skip - developers can handle their own)
check_development() {
    print_section "🔍 Checking development installations..."
    
    # Look for editable installs only
    if pip list --editable 2>/dev/null | grep -q boxofports; then
        local path=$(pip show boxofports | grep "Location:" | cut -d' ' -f2 || echo "unknown")
        add_detection "install" "$path" "pip editable install (development)" "pip_editable"
        echo -e "  ${RED}✓${NC} Found pip editable install: $path"
    else
        echo -e "  ${YELLOW}ℹ${NC} No development installations found (developers can handle their own)"
    fi
}

# Check for configuration and data directories (only recommended locations)
check_configs_and_data() {
    print_section "🔍 Checking configuration and data directories..."
    
    # Configuration directories (only the main one we recommend)
    if [[ -d "$HOME/.boxofports" ]]; then
        local files=$(ls -1 "$HOME/.boxofports" 2>/dev/null | wc -l | tr -d ' ')
        add_detection "config" "$HOME/.boxofports" "config directory ($files files)" "config"
        echo -e "  ${YELLOW}✓${NC} Found config directory: $HOME/.boxofports ($files files)"
    fi
    
    # Check if there are other config directories
    local other_config_paths=(
        "$HOME/.config/boxofports"
        "$HOME/Library/Application Support/boxofports"
    )
    
    for path in "${other_config_paths[@]}"; do
        if [[ -d "$path" ]]; then
            local files=$(ls -1 "$path" 2>/dev/null | wc -l | tr -d ' ')
            add_detection "config" "$path" "alternate config directory ($files files)" "config"
            echo -e "  ${YELLOW}✓${NC} Found alternate config directory: $path ($files files)"
        fi
    done
}

# Check for Docker images
check_docker_images() {
    print_section "🔍 Checking Docker images..."
    
    if command -v docker >/dev/null 2>&1; then
        # Check specifically for our recommended images
        local expected_images=(
            "altheasignals/boxofports:latest"
            "altheasignals/boxofports"
            "boxofports"
        )
        
        for image_pattern in "${expected_images[@]}"; do
            local images=$(docker images --filter "reference=$image_pattern" --format "{{.Repository}}:{{.Tag}} {{.Size}}" 2>/dev/null || true)
            if [[ -n "$images" ]]; then
                while IFS= read -r line; do
                    if [[ -n "$line" ]]; then
                        local image=$(echo "$line" | awk '{print $1}')
                        local size=$(echo "$line" | awk '{print $2}')
                        add_detection "install" "docker:$image" "Docker image ($size)" "docker_image"
                        echo -e "  ${BLUE}✓${NC} Found Docker image: $image ($size)"
                    fi
                done <<< "$images"
            fi
        done
    else
        echo -e "  ${YELLOW}ℹ${NC} Docker not found or not running"
    fi
}

# Display all detected installations
display_summary() {
    print_section "📋 Summary of Detected Installations"
    
    if [[ ${#DETECTED_INSTALLATIONS[@]} -eq 0 ]] && [[ ${#DETECTED_CONFIGS[@]} -eq 0 ]] && [[ ${#DETECTED_DATA[@]} -eq 0 ]]; then
        echo -e "${GREEN}No BoxOfPorts installations found!${NC}"
        return 0
    fi
    
    if [[ ${#DETECTED_INSTALLATIONS[@]} -gt 0 ]]; then
        echo -e "\n${RED}📦 Installations:${NC}"
        local i=1
        for detection in "${DETECTED_INSTALLATIONS[@]}"; do
            IFS='|' read -r path description method <<< "$detection"
            echo "  $i) $description"
            echo "     Path: $path"
            echo "     Type: $method"
            echo
            ((i++))
        done
    fi
    
    if [[ ${#DETECTED_CONFIGS[@]} -gt 0 ]]; then
        echo -e "\n${YELLOW}⚙️  Configuration:${NC}"
        local i=1
        for detection in "${DETECTED_CONFIGS[@]}"; do
            IFS='|' read -r path description method <<< "$detection"
            echo "  $i) $description"
            echo "     Path: $path"
            ((i++))
        done
    fi
    
    if [[ ${#DETECTED_DATA[@]} -gt 0 ]]; then
        echo -e "\n${BLUE}💾 Data:${NC}"
        local i=1
        for detection in "${DETECTED_DATA[@]}"; do
            IFS='|' read -r path description method <<< "$detection"
            echo "  $i) $description"
            echo "     Path: $path"
            ((i++))
        done
    fi
}

# Interactive removal
interactive_removal() {
    if [[ ${#DETECTED_INSTALLATIONS[@]} -eq 0 ]] && [[ ${#DETECTED_CONFIGS[@]} -eq 0 ]] && [[ ${#DETECTED_DATA[@]} -eq 0 ]]; then
        return 0
    fi
    
    print_section "🗑️  Interactive Removal"
    echo "Choose what to remove (separate multiple choices with spaces, e.g., '1 3 5'):"
    echo
    
    # Build removal menu
    local menu_items=()
    local menu_descriptions=()
    
    if [[ ${#DETECTED_INSTALLATIONS[@]} -gt 0 ]]; then
        echo -e "${RED}Installations:${NC}"
        local i=1
        for detection in "${DETECTED_INSTALLATIONS[@]}"; do
            IFS='|' read -r path description method <<< "$detection"
            menu_items+=("install|$path|$method")
            menu_descriptions+=("$description")
            echo "  $i) $description"
            ((i++))
        done
        echo
    fi
    
    if [[ ${#DETECTED_CONFIGS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Configuration (⚠️  Will delete your settings):${NC}"
        for detection in "${DETECTED_CONFIGS[@]}"; do
            IFS='|' read -r path description method <<< "$detection"
            menu_items+=("config|$path|$method")
            menu_descriptions+=("$description")
            echo "  $i) $description"
            ((i++))
        done
        echo
    fi
    
    if [[ ${#DETECTED_DATA[@]} -gt 0 ]]; then
        echo -e "${BLUE}Data (⚠️  Will delete your data files):${NC}"
        for detection in "${DETECTED_DATA[@]}"; do
            IFS='|' read -r path description method <<< "$detection"
            menu_items+=("data|$path|$method")
            menu_descriptions+=("$description")
            echo "  $i) $description"
            ((i++))
        done
        echo
    fi
    
    echo "0) Exit without removing anything"
    echo "a) Remove all installations only (keep config/data)"
    echo "A) Remove EVERYTHING (installations, config, and data)"
    echo
    
    read -p "Enter your choices: " -r choices
    
    if [[ "$choices" == "0" ]] || [[ -z "$choices" ]]; then
        echo "No changes made."
        return 0
    fi
    
    # Handle special cases
    if [[ "$choices" == "a" ]]; then
        choices=$(seq 1 ${#DETECTED_INSTALLATIONS[@]} | tr '\n' ' ')
    elif [[ "$choices" == "A" ]]; then
        choices=$(seq 1 ${#menu_items[@]} | tr '\n' ' ')
    fi
    
    # Perform removals
    for choice in $choices; do
        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -le ${#menu_items[@]} ]] && [[ $choice -ge 1 ]]; then
            local item_index=$((choice - 1))
            local item="${menu_items[$item_index]}"
            local description="${menu_descriptions[$item_index]}"
            
            IFS='|' read -r type path method <<< "$item"
            
            echo -e "\n${RED}Removing:${NC} $description"
            echo "Path: $path"
            
            case "$method" in
                "pip_global")
                    pip uninstall boxofports -y || echo "Failed to uninstall via pip"
                    ;;
                "pip_user")
                    pip uninstall --user boxofports -y || echo "Failed to uninstall via pip --user"
                    ;;
                "pip_editable")
                    pip uninstall boxofports -y || echo "Failed to uninstall editable install"
                    ;;
                "conda")
                    echo "Please manually remove from conda environment: $path"
                    ;;
                "docker_wrapper"|"unknown")
                    if [[ -f "$path" ]]; then
                        rm -f "$path" && echo "✓ Removed: $path" || echo "✗ Failed to remove: $path"
                    fi
                    ;;
                "docker_image")
                    local image_name=${path#docker:}
                    docker rmi "$image_name" 2>/dev/null && echo "✓ Removed Docker image: $image_name" || echo "✗ Failed to remove Docker image: $image_name"
                    ;;
                "config"|"data"|"development")
                    if [[ -d "$path" ]]; then
                        echo -n "⚠️  About to delete directory: $path - are you sure? [y/N]: "
                        read -r confirm
                        if [[ "$confirm" =~ ^[Yy]$ ]]; then
                            rm -rf "$path" && echo "✓ Removed: $path" || echo "✗ Failed to remove: $path"
                        else
                            echo "Skipped: $path"
                        fi
                    fi
                    ;;
            esac
        fi
    done
    
    echo -e "\n${GREEN}Removal process completed!${NC}"
}

# Usage function
usage() {
    cat <<EOF
BoxOfPorts Uninstaller

Usage: $0 [OPTIONS]

Options:
  --list-only    Only detect and list installations, don't offer removal
  --auto-docker  Automatically remove Docker wrapper and images
  --help, -h     Show this help message

Examples:
  $0                    # Interactive mode
  $0 --list-only        # Just show what's installed
  $0 --auto-docker      # Remove Docker installations automatically
EOF
}

# Main execution
main() {
    local LIST_ONLY=false
    local AUTO_DOCKER=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --list-only)
                LIST_ONLY=true
                shift
                ;;
            --auto-docker)
                AUTO_DOCKER=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # Run all detection checks
    check_pip_installations
    check_conda_installations
    check_docker_wrapper
    check_development
    check_configs_and_data
    check_docker_images
    
    # Display results
    display_summary
    
    if [[ "$LIST_ONLY" == "true" ]]; then
        exit 0
    fi
    
    if [[ "$AUTO_DOCKER" == "true" ]]; then
        echo -e "\n${YELLOW}Auto-removing Docker installations...${NC}"
        # Remove Docker wrappers and images automatically
        for detection in "${DETECTED_INSTALLATIONS[@]}"; do
            IFS='|' read -r path description method <<< "$detection"
            if [[ "$method" == "docker_wrapper" ]] || [[ "$method" == "docker_image" ]]; then
                if [[ "$method" == "docker_wrapper" ]] && [[ -f "$path" ]]; then
                    rm -f "$path" && echo "✓ Removed: $path"
                elif [[ "$method" == "docker_image" ]]; then
                    local image_name=${path#docker:}
                    docker rmi "$image_name" 2>/dev/null && echo "✓ Removed Docker image: $image_name"
                fi
            fi
        done
        exit 0
    fi
    
    # Interactive mode
    interactive_removal
}

# Run main function with all arguments
main "$@"