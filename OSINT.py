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


# =========================
# GRAPH ENGINE
# =========================
GRAPH = {"nodes": set(), "edges": []}

def add_node(n):
    GRAPH["nodes"].add(n)

def add_edge(a, b):
    GRAPH["edges"].append({"from": a, "to": b, "weight": 1})


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
        return r
    except:
        return {}


# =========================
# DOMAIN INTEL
# =========================
@plugin("domain")
def domain_info(domain):
    try:
        whois = requests.get(f"https://api.hackertarget.com/whois/?q={domain}").text
        dns = requests.get(f"https://api.hackertarget.com/dnslookup/?q={domain}").text

        data = {"whois": whois, "dns": dns}
        save(domain, "domain", data)
        return data
    except:
        return "error"


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
# TELEGRAM INTEL (ADDED)
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

    if "error" in str(data):
        score += 20
    if "FOUND" in str(data):
        score += 40
    if len(str(data)) > 1000:
        score += 10

    return {
        "risk_score": score,
        "level": "HIGH" if score > 60 else "MEDIUM" if score > 30 else "LOW"
    }


# =========================
# FULL SCAN ENGINE
# =========================
def full_scan(target):
    result = {}

    for name, func in PLUGINS.items():
        result[name] = func(target)

    # TELEGRAM INCLUDED
    result["telegram"] = telegram_scan(target)

    try:
        asyncio.run(async_social(target))
    except:
        pass

    save(target, "full_scan", result)

    return {
        "data": result,
        "ai": ai_analyze(result)
    }


# =========================
# FASTAPI SOC PANEL
# =========================
app = FastAPI()

@app.get("/")
def home():
    return {"status": "GOD MODE OSINT ACTIVE"}

@app.get("/scan/{target}")
def scan(target: str):
    return {
        "target": target,
        "result": full_scan(target),
        "graph": {
            "nodes": list(GRAPH["nodes"]),
            "edges": GRAPH["edges"]
        }
    }

@app.get("/email/{email}")
def email(email: str):
    return email_scan(email)

@app.get("/telegram/{username}")
def telegram(username: str):
    return telegram_scan(username)

@app.get("/graph")
def graph():
    return GRAPH


# =========================
# CLI MENU
# =========================
def menu():
    while True:
        print("""
========================
🔥 OSINT GOD MODE v2
========================
1. Full Scan
2. Social
3. IP Info
4. Domain Info
5. Email Scan
6. Telegram Scan
7. Exit
""")

        c = input("Select: ")

        if c == "1":
            print(full_scan(input("Target: ")))

        elif c == "2":
            print(social(input("Username: ")))

        elif c == "3":
            print(ip_info(input("IP: ")))

        elif c == "4":
            print(domain_info(input("Domain: ")))

        elif c == "5":
            print(email_scan(input("Email: ")))

        elif c == "6":
            print(telegram_scan(input("Telegram username: ")))

        elif c == "7":
            break


# =========================
# START SYSTEM
# =========================
if __name__ == "__main__":
    init_db()

    threading.Thread(target=menu, daemon=True).start()

    uvicorn.run(app, host="0.0.0.0", port=8000)
