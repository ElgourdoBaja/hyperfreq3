#!/bin/bash

# HyperFreq - Freqtrade Configuration Script for Hyperliquid
# This script helps configure Freqtrade for Hyperliquid trading

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FREQTRADE_DIR="/app/freqtrade"
USER_DATA_DIR="$FREQTRADE_DIR/user_data"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}        HyperFreq Configuration${NC}"
echo -e "${BLUE}  Freqtrade for Hyperliquid Trading${NC}"
echo -e "${BLUE}==========================================${NC}"
echo

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to prompt for input
prompt_input() {
    local prompt="$1"
    local var_name="$2"
    local default_value="$3"
    local is_secret="$4"
    
    if [ "$is_secret" = "true" ]; then
        echo -n "$prompt: "
        read -s input_value
        echo
    else
        if [ -n "$default_value" ]; then
            echo -n "$prompt [$default_value]: "
        else
            echo -n "$prompt: "
        fi
        read input_value
    fi
    
    if [ -z "$input_value" ] && [ -n "$default_value" ]; then
        input_value="$default_value"
    fi
    
    eval "$var_name='$input_value'"
}

# Function to update config file
update_config() {
    local config_file="$1"
    local wallet_address="$2"
    local api_key="$3"
    local api_secret="$4"
    
    print_info "Updating configuration file: $config_file"
    
    # Create backup
    cp "$config_file" "$config_file.backup"
    
    # Update the configuration
    sed -i "s/YOUR_HYPERLIQUID_WALLET_ADDRESS/$wallet_address/g" "$config_file"
    sed -i "s/YOUR_HYPERLIQUID_API_KEY/$api_key/g" "$config_file"
    sed -i "s/YOUR_HYPERLIQUID_API_SECRET/$api_secret/g" "$config_file"
    
    print_success "Configuration updated successfully!"
}

# Function to validate Hyperliquid address
validate_wallet_address() {
    local address="$1"
    if [[ $address =~ ^0x[a-fA-F0-9]{40}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Main configuration function
configure_credentials() {
    print_info "Setting up Hyperliquid API credentials..."
    echo
    
    print_warning "Make sure you have obtained your Hyperliquid API credentials from:"
    print_warning "https://app.hyperliquid.xyz/API"
    echo
    
    # Get wallet address
    while true; do
        prompt_input "Enter your Hyperliquid main wallet address (0x...)" wallet_address ""
        if validate_wallet_address "$wallet_address"; then
            break
        else
            print_error "Invalid wallet address format. Please enter a valid Ethereum address (0x...)"
        fi
    done
    
    # Get API key
    prompt_input "Enter your Hyperliquid API key" api_key ""
    if [ -z "$api_key" ]; then
        print_error "API key is required!"
        exit 1
    fi
    
    # Get API secret
    prompt_input "Enter your Hyperliquid API secret key" api_secret "" "true"
    if [ -z "$api_secret" ]; then
        print_error "API secret is required!"
        exit 1
    fi
    
    echo
    print_info "Credentials collected successfully!"
    echo
    
    # Ask which environment to configure
    echo "Which environment would you like to configure?"
    echo "1) Testnet (recommended for first-time setup)"
    echo "2) Mainnet (live trading with real funds)"
    echo "3) Both"
    echo
    prompt_input "Enter your choice [1-3]" env_choice "1"
    
    case $env_choice in
        1)
            update_config "$USER_DATA_DIR/config_hyperliquid_testnet.json" "$wallet_address" "$api_key" "$api_secret"
            print_success "Testnet configuration completed!"
            ;;
        2)
            update_config "$USER_DATA_DIR/config_hyperliquid_mainnet.json" "$wallet_address" "$api_key" "$api_secret"
            print_success "Mainnet configuration completed!"
            print_warning "CAUTION: You are now configured for live trading with real funds!"
            ;;
        3)
            update_config "$USER_DATA_DIR/config_hyperliquid_testnet.json" "$wallet_address" "$api_key" "$api_secret"
            update_config "$USER_DATA_DIR/config_hyperliquid_mainnet.json" "$wallet_address" "$api_key" "$api_secret"
            print_success "Both testnet and mainnet configurations completed!"
            ;;
        *)
            print_error "Invalid choice!"
            exit 1
            ;;
    esac
}

# Function to run Freqtrade
run_freqtrade() {
    local environment="$1"
    local config_file
    
    if [ "$environment" = "testnet" ]; then
        config_file="$USER_DATA_DIR/config_hyperliquid_testnet.json"
    elif [ "$environment" = "mainnet" ]; then
        config_file="$USER_DATA_DIR/config_hyperliquid_mainnet.json"
    else
        print_error "Invalid environment: $environment"
        exit 1
    fi
    
    if [ ! -f "$config_file" ]; then
        print_error "Configuration file not found: $config_file"
        print_info "Please run the configuration first: ./configure.sh"
        exit 1
    fi
    
    print_info "Starting Freqtrade with $environment configuration..."
    cd "$FREQTRADE_DIR"
    
    # Check if this is a dry run or live trading
    if [ "$environment" = "testnet" ]; then
        print_warning "Starting in TESTNET mode - safe for testing!"
    else
        print_warning "Starting in MAINNET mode - LIVE TRADING WITH REAL FUNDS!"
        echo
        prompt_input "Are you sure you want to continue? (yes/no)" confirm "no"
        if [ "$confirm" != "yes" ]; then
            print_info "Aborting..."
            exit 0
        fi
    fi
    
    python -m freqtrade trade --config "$config_file" --verbosity 3
}

# Function to download historical data
download_data() {
    local environment="$1"
    local config_file
    
    if [ "$environment" = "testnet" ]; then
        config_file="$USER_DATA_DIR/config_hyperliquid_testnet.json"
    elif [ "$environment" = "mainnet" ]; then
        config_file="$USER_DATA_DIR/config_hyperliquid_mainnet.json"
    else
        print_error "Invalid environment: $environment"
        exit 1
    fi
    
    print_info "Downloading historical data for backtesting..."
    cd "$FREQTRADE_DIR"
    
    python -m freqtrade download-data --config "$config_file" --timerange 20241201- --timeframes 1m 5m 15m 1h 4h 1d
}

# Function to run backtesting
run_backtest() {
    local environment="$1"
    local config_file
    
    if [ "$environment" = "testnet" ]; then
        config_file="$USER_DATA_DIR/config_hyperliquid_testnet.json"
    elif [ "$environment" = "mainnet" ]; then
        config_file="$USER_DATA_DIR/config_hyperliquid_mainnet.json"
    else
        print_error "Invalid environment: $environment"
        exit 1
    fi
    
    print_info "Running backtest..."
    cd "$FREQTRADE_DIR"
    
    python -m freqtrade backtesting --config "$config_file" --strategy MovingAverageCrossStrategy --timerange 20241201-
}

# Function to show status
show_status() {
    print_info "HyperFreq Status:"
    echo
    
    # Check if configurations exist
    if [ -f "$USER_DATA_DIR/config_hyperliquid_testnet.json" ]; then
        if grep -q "YOUR_HYPERLIQUID" "$USER_DATA_DIR/config_hyperliquid_testnet.json"; then
            print_warning "Testnet: Not configured (placeholders found)"
        else
            print_success "Testnet: Configured"
        fi
    else
        print_error "Testnet: Configuration file missing"
    fi
    
    if [ -f "$USER_DATA_DIR/config_hyperliquid_mainnet.json" ]; then
        if grep -q "YOUR_HYPERLIQUID" "$USER_DATA_DIR/config_hyperliquid_mainnet.json"; then
            print_warning "Mainnet: Not configured (placeholders found)"
        else
            print_success "Mainnet: Configured"
        fi
    else
        print_error "Mainnet: Configuration file missing"
    fi
    
    echo
    
    # Check if strategy exists
    if [ -f "$USER_DATA_DIR/strategies/MovingAverageCrossStrategy.py" ]; then
        print_success "Strategy: MovingAverageCrossStrategy.py available"
    else
        print_error "Strategy: MovingAverageCrossStrategy.py missing"
    fi
    
    echo
    
    # Show recent log entries if any
    if [ -f "$USER_DATA_DIR/logs/freqtrade.log" ]; then
        print_info "Recent log entries:"
        tail -n 5 "$USER_DATA_DIR/logs/freqtrade.log" 2>/dev/null || print_warning "No recent logs found"
    else
        print_info "No log file found yet"
    fi
}

# Main menu
show_menu() {
    echo
    echo "What would you like to do?"
    echo
    echo "1) Configure API credentials"
    echo "2) Run Freqtrade (Testnet)"
    echo "3) Run Freqtrade (Mainnet)"
    echo "4) Download historical data (Testnet)"
    echo "5) Download historical data (Mainnet)"
    echo "6) Run backtest (Testnet)"
    echo "7) Run backtest (Mainnet)"
    echo "8) Show status"
    echo "9) Exit"
    echo
    prompt_input "Enter your choice [1-9]" choice "1"
    
    case $choice in
        1) configure_credentials ;;
        2) run_freqtrade "testnet" ;;
        3) run_freqtrade "mainnet" ;;
        4) download_data "testnet" ;;
        5) download_data "mainnet" ;;
        6) run_backtest "testnet" ;;
        7) run_backtest "mainnet" ;;
        8) show_status ;;
        9) print_info "Goodbye!"; exit 0 ;;
        *) print_error "Invalid choice!"; show_menu ;;
    esac
}

# Parse command line arguments
case "${1:-}" in
    "configure"|"config")
        configure_credentials
        ;;
    "run-testnet"|"testnet")
        run_freqtrade "testnet"
        ;;
    "run-mainnet"|"mainnet")
        run_freqtrade "mainnet"
        ;;
    "download-testnet")
        download_data "testnet"
        ;;
    "download-mainnet")
        download_data "mainnet"
        ;;
    "backtest-testnet")
        run_backtest "testnet"
        ;;
    "backtest-mainnet")
        run_backtest "mainnet"
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  configure       Configure API credentials"
        echo "  run-testnet     Run Freqtrade in testnet mode"
        echo "  run-mainnet     Run Freqtrade in mainnet mode"
        echo "  download-testnet Download historical data for testnet"
        echo "  download-mainnet Download historical data for mainnet"
        echo "  backtest-testnet Run backtest with testnet config"
        echo "  backtest-mainnet Run backtest with mainnet config"
        echo "  status          Show configuration status"
        echo "  help            Show this help message"
        echo
        echo "If no command is provided, the interactive menu will be shown."
        ;;
    "")
        show_menu
        ;;
    *)
        print_error "Unknown command: $1"
        print_info "Use '$0 help' to see available commands"
        exit 1
        ;;
esac