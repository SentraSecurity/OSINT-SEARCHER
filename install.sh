#!/bin/bash

echo "Installing OSINT GOD dependencies..."

# Ubuntu/Debian
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y sqlite3 curl jq dnsutils whois
    sudo apt install -y python3 python3-pip  # Python version uchun
fi

# Termux (Android)
if command -v pkg &> /dev/null; then
    pkg update
    pkg install -y sqlite curl jq dnsutils whois python
fi

# Python uchun (agar kerak bo'lsa)
pip3 install fastapi uvicorn requests aiohttp

echo "✅ All dependencies installed!"
