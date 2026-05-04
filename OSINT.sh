#!/bin/bash

# ======================================
# OSINT GOD MODE - BASH SCRIPT
# ======================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Database file
DB_FILE="osint_god.db"

# ======================================
# FUNCTIONS
# ======================================

init_db() {
    sqlite3 "$DB_FILE" "CREATE TABLE IF NOT EXISTS intel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT,
        module TEXT,
        data TEXT,
        timestamp TEXT
    );"
}

save_result() {
    local target=$1
    local module=$2
    local data=$3
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    sqlite3 "$DB_FILE" "INSERT INTO intel (target, module, data, timestamp) 
                        VALUES ('$target', '$module', '$data', '$timestamp');"
}

show_banner() {
    clear
    echo -e "${RED}"
    echo "    ╔══════════════════════════════════════════════════════════╗"
    echo "    ║                    🔥 OSINT GOD MODE v2.0               ║"
    echo "    ║              Advanced OSINT Framework - Bash             ║"
    echo "    ╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Social Media Scan
social_scan() {
    local username=$1
    echo -e "\n${YELLOW}[+] Scanning social media for: $username${NC}\n"
    
    local sites=(
        "GitHub:https://github.com/$username"
        "Twitter:https://twitter.com/$username"
        "Instagram:https://instagram.com/$username"
        "Reddit:https://reddit.com/user/$username"
        "TikTok:https://www.tiktok.com/@$username"
    )
    
    local results=""
    for site in "${sites[@]}"; do
        name=$(echo $site | cut -d':' -f1)
        url=$(echo $site | cut -d':' -f2-)
        
        status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
        
        if [[ "$status" == "200" ]]; then
            echo -e "  ${GREEN}✓${NC} $name: ${GREEN}FOUND${NC} ($status)"
            results="$results\n$name: FOUND"
        else
            echo -e "  ${RED}✗${NC} $name: ${RED}NOT FOUND${NC} ($status)"
            results="$results\n$name: NOT FOUND"
        fi
    done
    
    save_result "$username" "social" "$results"
    echo -e "\n${GREEN}[✓] Results saved to database${NC}"
}

# IP Scan
ip_scan() {
    local ip=$1
    echo -e "\n${YELLOW}[+] Scanning IP: $ip${NC}\n"
    
    response=$(curl -s "http://ip-api.com/json/$ip")
    
    if [[ -n "$response" ]]; then
        country=$(echo "$response" | jq -r '.country // "N/A"')
        city=$(echo "$response" | jq -r '.city // "N/A"')
        isp=$(echo "$response" | jq -r '.isp // "N/A"')
        lat=$(echo "$response" | jq -r '.lat // "N/A"')
        lon=$(echo "$response" | jq -r '.lon // "N/A"')
        
        echo -e "  ${CYAN}📍 Location:${NC} $city, $country"
        echo -e "  ${CYAN}🏢 ISP:${NC} $isp"
        echo -e "  ${CYAN}🗺️  Coordinates:${NC} $lat, $lon"
        
        save_result "$ip" "ip" "$response"
        echo -e "\n${GREEN}[✓] Results saved to database${NC}"
    else
        echo -e "${RED}[!] IP lookup failed${NC}"
    fi
}

# Domain Scan
domain_scan() {
    local domain=$1
    echo -e "\n${YELLOW}[+] Scanning domain: $domain${NC}\n"
    
    # DNS Lookup
    echo -e "${CYAN}📡 DNS Records:${NC}"
    dns_result=$(dig +short "$domain" 2>/dev/null)
    if [[ -n "$dns_result" ]]; then
        echo "$dns_result" | while read line; do
            echo -e "  → $line"
        done
    else
        echo -e "  ${RED}No DNS records found${NC}"
    fi
    
    # WHOIS (simplified)
    echo -e "\n${CYAN}📋 WHOIS Info:${NC}"
    whois_result=$(whois "$domain" 2>/dev/null | head -20)
    if [[ -n "$whois_result" ]]; then
        echo "$whois_result" | while read line; do
            echo -e "  $line"
        done
    else
        echo -e "  ${RED}WHOIS lookup failed${NC}"
    fi
    
    save_result "$domain" "domain" "$dns_result"
    echo -e "\n${GREEN}[✓] Results saved to database${NC}"
}

# Email Scan
email_scan() {
    local email=$1
    echo -e "\n${YELLOW}[+] Scanning email: $email${NC}\n"
    
    # Validate email format
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        echo -e "  ${GREEN}✓${NC} Email format: ${GREEN}VALID${NC}"
        
        domain=$(echo "$email" | cut -d'@' -f2)
        echo -e "  ${CYAN}🏠 Domain:${NC} $domain"
        
        # Check breach (using public API)
        breach_check=$(curl -s "https://api.xposedornot.com/v1/breach-analytics?email=$email" 2>/dev/null)
        
        if [[ -n "$breach_check" ]]; then
            echo -e "  ${CYAN}🔓 Breach Check:${NC} Completed"
        fi
    else
        echo -e "  ${RED}✗${NC} Email format: ${RED}INVALID${NC}"
    fi
    
    save_result "$email" "email" "Scanned"
    echo -e "\n${GREEN}[✓] Results saved to database${NC}"
}

# Telegram Scan
telegram_scan() {
    local username=$1
    echo -e "\n${YELLOW}[+] Scanning Telegram: @$username${NC}\n"
    
    url="https://t.me/$username"
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
    
    if [[ "$status" == "200" ]]; then
        echo -e "  ${GREEN}✓${NC} Profile: ${GREEN}FOUND${NC}"
        echo -e "  ${CYAN}🔗 URL:${NC} $url"
    else
        echo -e "  ${RED}✗${NC} Profile: ${RED}NOT FOUND${NC}"
    fi
    
    save_result "$username" "telegram" "Status: $status"
    echo -e "\n${GREEN}[✓] Results saved to database${NC}"
}

# Full Scan
full_scan() {
    local target=$1
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}              🎯 FULL SCAN: $target${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
    
    social_scan "$target"
    ip_scan "$target"
    domain_scan "$target"
    email_scan "$target"
    telegram_scan "$target"
    
    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}              ✅ FULL SCAN COMPLETED${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
}

# Show History
show_history() {
    echo -e "\n${YELLOW}[+] Recent Scan History${NC}\n"
    
    sqlite3 "$DB_FILE" "SELECT target, module, timestamp FROM intel ORDER BY timestamp DESC LIMIT 20;" 2>/dev/null | while IFS='|' read target module timestamp; do
        echo -e "  ${CYAN}[$timestamp]${NC} $target → ${GREEN}$module${NC}"
    done
    
    if [[ $? -ne 0 ]]; then
        echo -e "  ${RED}No history found${NC}"
    fi
}

# Show Stats
show_stats() {
    echo -e "\n${YELLOW}[+] Statistics${NC}\n"
    
    total=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM intel;" 2>/dev/null)
    echo -e "  ${CYAN}📊 Total Scans:${NC} $total"
    
    echo -e "\n${CYAN}📁 By Module:${NC}"
    sqlite3 "$DB_FILE" "SELECT module, COUNT(*) FROM intel GROUP BY module;" 2>/dev/null | while IFS='|' read module count; do
        echo -e "    → $module: $count"
    done
}

# Export Results
export_results() {
    local filename="osint_export_$(date '+%Y%m%d_%H%M%S').json"
    
    echo -e "\n${YELLOW}[+] Exporting results to $filename${NC}\n"
    
    sqlite3 "$DB_FILE" "SELECT json_group_array(
        json_object('target', target, 'module', module, 'data', data, 'timestamp', timestamp)
    ) FROM intel;" 2>/dev/null > "$filename"
    
    if [[ -f "$filename" ]]; then
        echo -e "${GREEN}[✓] Exported to $filename${NC}"
    else
        echo -e "${RED}[!] Export failed${NC}"
    fi
}

# ======================================
# MAIN MENU
# ======================================

main_menu() {
    while true; do
        show_banner
        echo -e "${WHITE}"
        echo "    ┌─────────────────────────────────────────────────────────┐"
        echo "    │                    📡 MAIN MENU                         │"
        echo "    ├─────────────────────────────────────────────────────────┤"
        echo "    │  1. 🎯 Full Scan (All Modules)                          │"
        echo "    │  2. 📱 Social Media Scan                                │"
        echo "    │  3. 🌐 IP Intelligence                                  │"
        echo "    │  4. 🔗 Domain Intelligence                              │"
        echo "    │  5. ✉️  Email Scan                                      │"
        echo "    │  6. 💬 Telegram Profile Scan                            │"
        echo "    │  7. 📊 View History                                     │"
        echo "    │  8. 📈 Statistics                                       │"
        echo "    │  9. 💾 Export Results                                   │"
        echo "    │  10. 🗑️  Clear Screen                                   │"
        echo "    │  11. 🚪 Exit                                            │"
        echo "    └─────────────────────────────────────────────────────────┘"
        echo -e "${NC}"
        
        read -p "    ⚡ Select option [1-11]: " choice
        
        case $choice in
            1)
                read -p "    🎯 Enter target (username/ip/domain/email): " target
                full_scan "$target"
                ;;
            2)
                read -p "    📱 Enter username: " username
                social_scan "$username"
                ;;
            3)
                read -p "    🌐 Enter IP address: " ip
                ip_scan "$ip"
                ;;
            4)
                read -p "    🔗 Enter domain: " domain
                domain_scan "$domain"
                ;;
            5)
                read -p "    ✉️  Enter email: " email
                email_scan "$email"
                ;;
            6)
                read -p "    💬 Enter Telegram username: " username
                telegram_scan "$username"
                ;;
            7)
                show_history
                ;;
            8)
                show_stats
                ;;
            9)
                export_results
                ;;
            10)
                clear
                show_banner
                ;;
            11)
                echo -e "\n    ${GREEN}👋 Goodbye!${NC}\n"
                exit 0
                ;;
            *)
                echo -e "\n    ${RED}❌ Invalid option!${NC}"
                ;;
        esac
        
        echo -e "\n"
        read -p "    Press Enter to continue..."
    done
}

# ======================================
# START
# ======================================

# Check dependencies
check_deps() {
    local deps=("sqlite3" "curl" "jq" "dig")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "${RED}[!] Missing dependencies: ${missing[*]}${NC}"
        echo -e "${YELLOW}Install with: sudo apt install sqlite3 curl jq dnsutils${NC}"
        exit 1
    fi
}

check_deps
init_db
main_menu
