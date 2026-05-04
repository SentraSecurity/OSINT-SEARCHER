import os
import json
import sqlite3
import threading
import requests
import asyncio
import re
from datetime import datetime
from fastapi import FastAPI
import uvicorn
import aiohttp

# =========================
# CORE DB
# =========================
DB = "osint_god.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS intel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT,
        module TEXT,
        data TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def save(target, module, data):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO intel VALUES (NULL,?,?,?,?)",
              (target, module, json.dumps(data), str(datetime.now())))
    conn.commit()
    conn.close()

def get_history(target=None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if target:
        c.execute("SELECT target, module, data, timestamp FROM intel WHERE target=? ORDER BY timestamp DESC", (target,))
    else:
        c.execute("SELECT target, module, data, timestamp FROM intel ORDER BY timestamp DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return [{"target": r[0], "module": r[1], "data": json.loads(r[2]), "timestamp": r[3]} for r in rows]

# =========================
# GRAPH ENGINE
# =========================
GRAPH = {"nodes": set(), "edges": []}

def add_node(n):
    GRAPH["nodes"].add(n)

def add_edge(a, b):
    GRAPH["edges"].append({"from": a, "to": b, "weight": 1})

def get_graph():
    return {"nodes": list(GRAPH["nodes"]), "edges": GRAPH["edges"]}

# =========================
# PLUGIN SYSTEM
# =========================
PLUGINS = {}

def plugin(name):
    def wrapper(func):
        PLUGINS[name] = func
        return func
    return wrapper

# =========================
# SOCIAL INTEL
# =========================
@plugin("social")
def social(username):
    sites = [
        f"https://github.com/{username}",
        f"https://twitter.com/{username}",
        f"https://instagram.com/{username}",
        f"https://reddit.com/user/{username}",
        f"https://www.tiktok.com/@{username}"
    ]
    
    res = {}  
    for s in sites:  
        try:  
            r = requests.get(s, timeout=5)  
            res[s] = r.status_code  
        except:  
            res[s] = "error"  
    
    save(username, "social", res)  
    add_node(username)  
    add_node("social")  
    add_edge("social", username)  
    return res

# =========================
# IP INTEL
# =========================
@plugin("ip")
def ip_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        save(ip, "ip", r)
        add_node(ip)
        add_node("ip")
        add_edge("ip", ip)
        return r
    except:
        return {"error": "IP lookup failed"}

# =========================
# DOMAIN INTEL
# =========================
@plugin("domain")
def domain_info(domain):
    try:
        whois = requests.get(f"https://api.hackertarget.com/whois/?q={domain}").text
        dns = requests.get(f"https://api.hackertarget.com/dnslookup/?q={domain}").text
        data = {"whois": whois[:500], "dns": dns[:500]}  
        save(domain, "domain", data)  
        add_node(domain)
        add_node("domain")
        add_edge("domain", domain)
        return data  
    except:  
        return {"error": "Domain lookup failed"}

# =========================
# EMAIL INTEL
# =========================
@plugin("email")
def email_scan(email):
    result = {
        "email": email,
        "valid": False,
        "breach": None
    }
    
    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):  
        result["valid"] = True  
        try:  
            r = requests.get(  
                f"https://api.xposedornot.com/v1/breach-analytics?email={email}",  
                timeout=5  
            ).json()  
            result["breach"] = r  
        except:  
            result["breach"] = "no data"  
    
    save(email, "email", result)  
    add_node(email)  
    if result["valid"]:  
        domain = email.split("@")[1]  
        add_node(domain)  
        add_edge(email, domain)  
    return result

# =========================
# TELEGRAM INTEL
# =========================
@plugin("telegram")
def telegram_scan(username):
    url = f"https://t.me/{username}"
    
    result = {  
        "username": username,  
        "url": url,  
        "status": "unknown"  
    }  
    
    try:  
        r = requests.get(url, timeout=5)  
        if r.status_code == 200:  
            result["status"] = "FOUND"  
        else:  
            result["status"] = "NOT FOUND"  
    except:  
        result["status"] = "ERROR"  
    
    save(username, "telegram", result)  
    add_node(username)  
    add_node("telegram")  
    add_edge("telegram", username)  
    return result

# =========================
# USERNAME MULTI-SCAN
# =========================
@plugin("username")
def username_scan(username):
    results = {
        "social": social(username),
        "telegram": telegram_scan(username)
    }
    save(username, "username", results)
    return results

# =========================
# ASYNC ENGINE
# =========================
async def fetch(session, url):
    try:
        async with session.get(url, timeout=5) as r:
            return await r.text()
    except:
        return "error"

async def async_social(username):
    urls = [
        f"https://github.com/{username}",
        f"https://twitter.com/{username}",
        f"https://instagram.com/{username}"
    ]
    async with aiohttp.ClientSession() as session:  
        tasks = [fetch(session, u) for u in urls]  
        return await asyncio.gather(*tasks)

# =========================
# AI ANALYZER
# =========================
def ai_analyze(data):
    score = 0
    data_str = str(data).lower()
    
    if "error" in data_str:  
        score += 20  
    if "found" in data_str or "200" in data_str:  
        score += 40  
    if len(data_str) > 1000:  
        score += 10  
    if "breach" in data_str and "data" in data_str:
        score += 30
    
    return {  
        "risk_score": min(score, 100),  
        "level": "HIGH" if score > 60 else "MEDIUM" if score > 30 else "LOW"  
    }

# =========================
# FULL SCAN ENGINE
# =========================
def full_scan(target):
    result = {}
    for name, func in PLUGINS.items():  
        try:
            result[name] = func(target)
        except:
            result[name] = {"error": f"{name} scan failed"}
    
    save(target, "full_scan", result)  
    return {  
        "data": result,  
        "ai": ai_analyze(result)  
    }

# =========================
# FASTAPI SOC PANEL
# =========================
app = FastAPI(title="OSINT GOD MODE", description="OSINT Framework with Web & CLI")

@app.get("/")
def home():
    return {"status": "GOD MODE OSINT ACTIVE", "modules": list(PLUGINS.keys())}

@app.get("/scan/{target}")
def scan(target: str):
    return {
        "target": target,
        "result": full_scan(target),
        "graph": get_graph()
    }

@app.get("/email/{email}")
def email(email: str):
    return email_scan(email)

@app.get("/telegram/{username}")
def telegram(username: str):
    return telegram_scan(username)

@app.get("/ip/{ip}")
def ip(ip: str):
    return ip_info(ip)

@app.get("/domain/{domain}")
def domain(domain: str):
    return domain_info(domain)

@app.get("/social/{username}")
def social_scan(username: str):
    return social(username)

@app.get("/graph")
def graph():
    return get_graph()

@app.get("/history")
def history(target: str = None):
    return get_history(target)

# =========================
# BASH STYLE MENU
# =========================
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                    🔥 OSINT GOD MODE v2.0               ║
    ║              Advanced OSINT Framework with Web UI        ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def menu():
    while True:
        clear_screen()
        print_banner()
        print("""
    ┌─────────────────────────────────────────────────────────┐
    │                    📡 MAIN MENU                         │
    ├─────────────────────────────────────────────────────────┤
    │  1. 🎯 Full Scan (All Modules)                          │
    │  2. 📱 Social Media Scan                                │
    │  3. 🌐 IP Intelligence                                  │
    │  4. 🔗 Domain Intelligence                              │
    │  5. ✉️  Email Scan (Breach Check)                       │
    │  6. 💬 Telegram Profile Scan                            │
    │  7. 👤 Multi-Scan (Social+TG)                           │
    │  8. 📊 View Graph (Relations)                           │
    │  9. 📜 History & Reports                                │
    │  10. 🧹 Clear Screen                                     │
    │  11. 🚪 Exit                                             │
    └─────────────────────────────────────────────────────────┘
        """)
        
        choice = input("    ⚡ Select option [1-11]: ").strip()
        
        if choice == "1":
            target = input("    🎯 Enter target (username/ip/domain/email): ").strip()
            print("\n    🔍 Scanning...\n")
            result = full_scan(target)
            print(f"\n    📊 RESULT for {target}:")
            print(f"    {'-'*50}")
            for mod, data in result["data"].items():
                print(f"    [{mod.upper()}] {str(data)[:100]}...")
            print(f"\n    🤖 AI RISK: {result['ai']['level']} (Score: {result['ai']['risk_score']})")
            input("\n    Press Enter to continue...")
            
        elif choice == "2":
            username = input("    📱 Enter username: ").strip()
            print("\n    🔍 Searching social media...\n")
            result = social(username)
            for site, status in result.items():
                print(f"    {site}: {status}")
            input("\n    Press Enter to continue...")
            
        elif choice == "3":
            ip = input("    🌐 Enter IP address: ").strip()
            print("\n    🔍 Looking up IP...\n")
            result = ip_info(ip)
            print(f"    {json.dumps(result, indent=2)[:500]}")
            input("\n    Press Enter to continue...")
            
        elif choice == "4":
            domain = input("    🔗 Enter domain: ").strip()
            print("\n    🔍 Looking up domain...\n")
            result = domain_info(domain)
            for k, v in result.items():
                print(f"    {k.upper()}: {str(v)[:200]}...")
            input("\n    Press Enter to continue...")
            
        elif choice == "5":
            email = input("    ✉️  Enter email: ").strip()
            print("\n    🔍 Scanning email...\n")
            result = email_scan(email)
            print(f"    Valid: {result['valid']}")
            print(f"    Breach Data: {result.get('breach', 'N/A')}")
            input("\n    Press Enter to continue...")
            
        elif choice == "6":
            username = input("    💬 Enter Telegram username: ").strip()
            print("\n    🔍 Checking Telegram...\n")
            result = telegram_scan(username)
            print(f"    Status: {result['status']}")
            print(f"    URL: {result['url']}")
            input("\n    Press Enter to continue...")
            
        elif choice == "7":
            username = input("    👤 Enter username: ").strip()
            print("\n    🔍 Multi-scanning...\n")
            result = username_scan(username)
            print(f"    Social: {result['social']}")
            print(f"    Telegram: {result['telegram']}")
            input("\n    Press Enter to continue...")
            
        elif choice == "8":
            print("\n    📊 Knowledge Graph:")
            print(f"    {'-'*50}")
            g = get_graph()
            print(f"    NODES ({len(g['nodes'])}): {', '.join(list(g['nodes'])[:20])}")
            print(f"    EDGES ({len(g['edges'])}):")
            for e in g['edges'][:15]:
                print(f"      {e['from']} → {e['to']}")
            input("\n    Press Enter to continue...")
            
        elif choice == "9":
            print("\n    📜 Recent History:")
            print(f"    {'-'*50}")
            history = get_history()
            for h in history[:15]:
                print(f"    [{h['timestamp'][:19]}] {h['target']} → {h['module']}")
            input("\n    Press Enter to continue...")
            
        elif choice == "10":
            clear_screen()
            
        elif choice == "11":
            print("\n    👋 Shutting down OSINT GOD MODE...\n")
            break
        
        else:
            print("\n    ❌ Invalid option!")
            input("    Press Enter to continue...")

# =========================
# START SYSTEM
# =========================
if __name__ == "__main__":
    init_db()
    
    print("    🚀 Starting OSINT GOD MODE...")
    print("    📡 Web UI: http://localhost:8000")
    print("    💻 CLI Menu Loading...\n")
    
    # Start web server in thread
    threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning"), daemon=True).start()
    
    # Start CLI menu
    menu()
