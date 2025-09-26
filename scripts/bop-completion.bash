#!/usr/bin/env bash
# BoxOfPorts Docker Wrapper (bop) completion script
# "Such a long long time to be gone, and a short time to be there"

_bop_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    local main_commands="sms ops status inbox config test-connection"
    
    # SMS subcommands
    local sms_commands="send spray"
    
    # Ops subcommands  
    local ops_commands="lock unlock"
    
    # Status subcommands
    local status_commands="subscribe"
    
    # Inbox subcommands
    local inbox_commands="list search stop summary show"
    
    # Config subcommands
    local config_commands="add-profile edit-profile list switch show remove current"
    
    # Global options
    local global_options="--host --port --user --password --pass --verbose -v --version --help -h"
    
    # SMS send/spray options
    local sms_options="--to --text --ports --repeat --intvl-ms --timeout --var --dry-run"
    
    # SMS spray specific options
    local spray_options="--to --text --ports --intvl-ms"
    
    # Status subscribe options
    local status_subscribe_options="--callback --period"
    
    # Inbox list options
    local inbox_list_options="--start-id --count --type --port --sender --contains --no-delivery-reports --delivery-reports-only --json"
    
    # Inbox search options
    local inbox_search_options="--start-id --count --details"
    
    # Inbox stop/summary options
    local inbox_stop_options="--start-id --json"
    local inbox_summary_options="--json"
    
    # Inbox show options
    local inbox_show_options="--start-id"
    
    # Config add-profile options
    local config_add_profile_options="--host --port --user --password --alias"
    
    # Operations options
    local ops_options="--ports"
    
    # Message types for --type option
    local message_types="regular stop system delivery_report keyword"
    
    # Common port patterns (examples)
    local port_examples="1A 1B 1C 1D 2A 2B 3A 4A 1A-1D 2A-2D 1A,2B,3C 1.01 2.02"
    
    case ${COMP_CWORD} in
        1)
            # First argument: main commands
            COMPREPLY=($(compgen -W "${main_commands} ${global_options}" -- ${cur}))
            return 0
            ;;
        2)
            # Second argument: subcommands or global options
            case "${prev}" in
                sms)
                    COMPREPLY=($(compgen -W "${sms_commands}" -- ${cur}))
                    return 0
                    ;;
                ops)
                    COMPREPLY=($(compgen -W "${ops_commands}" -- ${cur}))
                    return 0
                    ;;
                status)
                    COMPREPLY=($(compgen -W "${status_commands}" -- ${cur}))
                    return 0
                    ;;
                inbox)
                    COMPREPLY=($(compgen -W "${inbox_commands}" -- ${cur}))
                    return 0
                    ;;
                config)
                    COMPREPLY=($(compgen -W "${config_commands}" -- ${cur}))
                    return 0
                    ;;
                --host|--port|--user|--password|--pass)
                    # Don't offer completions for these values
                    return 0
                    ;;
                *)
                    COMPREPLY=($(compgen -W "${global_options}" -- ${cur}))
                    return 0
                    ;;
            esac
            ;;
        *)
            # Handle subcommand options and arguments
            local command_path=""
            local i=1
            while [[ $i -lt ${COMP_CWORD} ]]; do
                case "${COMP_WORDS[$i]}" in
                    --*|-*)
                        # Skip options and their values
                        if [[ "${COMP_WORDS[$i]}" =~ ^--(host|port|user|password|pass|to|text|ports|callback|type|sender|contains|start-id|count|repeat|intvl-ms|timeout|var)$ ]]; then
                            ((i++))  # Skip option value
                        fi
                        ;;
                    *)
                        if [[ -z "$command_path" ]]; then
                            command_path="${COMP_WORDS[$i]}"
                        else
                            command_path="$command_path ${COMP_WORDS[$i]}"
                        fi
                        ;;
                esac
                ((i++))
            done
            
            # Handle specific command completions
            case "$command_path" in
                "sms send")
                    case "${prev}" in
                        --type)
                            COMPREPLY=($(compgen -W "${message_types}" -- ${cur}))
                            ;;
                        --ports)
                            COMPREPLY=($(compgen -W "${port_examples}" -- ${cur}))
                            ;;
                        --to|--text|--repeat|--intvl-ms|--timeout|--var)
                            # No completion for these
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${sms_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "sms spray")
                    case "${prev}" in
                        --ports)
                            COMPREPLY=($(compgen -W "${port_examples}" -- ${cur}))
                            ;;
                        --to|--text|--intvl-ms)
                            # No completion for these
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${spray_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "ops lock"|"ops unlock")
                    case "${prev}" in
                        --ports)
                            COMPREPLY=($(compgen -W "${port_examples}" -- ${cur}))
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${ops_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "status subscribe")
                    case "${prev}" in
                        --callback|--period)
                            # No completion for these
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${status_subscribe_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "inbox list")
                    case "${prev}" in
                        --type)
                            COMPREPLY=($(compgen -W "${message_types}" -- ${cur}))
                            ;;
                        --port)
                            COMPREPLY=($(compgen -W "${port_examples}" -- ${cur}))
                            ;;
                        --start-id|--count|--sender|--contains)
                            # No completion for these
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${inbox_list_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "inbox search")
                    case "${prev}" in
                        --start-id|--count)
                            # No completion for these
                            ;;
                        search)
                            # First argument after "inbox search" is the search text
                            # No specific completion
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${inbox_search_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "inbox stop")
                    case "${prev}" in
                        --start-id)
                            # No completion
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${inbox_stop_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "inbox summary")
                    COMPREPLY=($(compgen -W "${inbox_summary_options}" -- ${cur}))
                    ;;
                "inbox show")
                    case "${prev}" in
                        --start-id)
                            # No completion
                            ;;
                        show)
                            # First argument after "inbox show" is the message ID
                            # No specific completion
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${inbox_show_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "config add-profile")
                    case "${prev}" in
                        --host|--port|--user|--password|--alias)
                            # No completion for these values
                            ;;
                        add-profile)
                            # First argument after "config add-profile" is the profile name
                            # No specific completion
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${config_add_profile_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "config edit-profile")
                    case "${prev}" in
                        --host|--port|--user|--password|--alias)
                            # No completion for these values
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "${config_add_profile_options}" -- ${cur}))
                            ;;
                    esac
                    ;;
                "config list")
                    # No additional options
                    ;;
                "config switch"|"config show"|"config remove")
                    case "${prev}" in
                        switch|show|remove)
                            # Try to get available profiles from bop config list
                            if command -v bop >/dev/null 2>&1; then
                                local profiles=$(bop config list 2>/dev/null | tail -n +2 | awk '{print $1}' | grep -v '^$' 2>/dev/null || echo "")
                                if [[ -n "$profiles" ]]; then
                                    COMPREPLY=($(compgen -W "${profiles}" -- ${cur}))
                                fi
                            fi
                            ;;
                    esac
                    ;;
                "config current")
                    # No additional options
                    ;;
                *)
                    # Default: offer global options
                    COMPREPLY=($(compgen -W "${global_options}" -- ${cur}))
                    ;;
            esac
            ;;
    esac
}

# Register the completion function
complete -F _bop_completion bop

# ZSH compatibility
if [[ -n ${ZSH_VERSION-} ]]; then
    autoload -U +X bashcompinit && bashcompinit
    complete -F _bop_completion bop
fi
