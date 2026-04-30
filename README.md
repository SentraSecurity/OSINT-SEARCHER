# 🔥 OSINT GOD MODE v2

Advanced Open-Source Intelligence (OSINT) platform built with **FastAPI backend + React dashboard + plugin-based reconnaissance engine**.

This project is designed for **cybersecurity research, threat intelligence, and OSINT learning purposes**.

---

## 🧠 Features

### ⚡ Intelligence Modules
- 🌐 Social media footprint scanning (GitHub, Twitter, Instagram, Reddit, TikTok)
- 📡 IP geolocation & network intelligence
- 🧾 Domain WHOIS + DNS enumeration
- 📧 Email validation + breach database check
- 📱 Telegram username OSINT scanner

---

### 🧠 Core Engine
- 🔌 Plugin-based architecture (easily extendable modules)
- 🕸 Relationship graph system (nodes + edges)
- ⚡ Async scanning engine (aiohttp support)
- 🤖 AI risk scoring system
- 💾 SQLite local intelligence database

---

### 🌐 API System (FastAPI SOC Panel)

| Endpoint | Description |
|----------|-------------|
| `/scan/{target}` | Full OSINT scan |
| `/email/{email}` | Email intelligence + breach check |
| `/telegram/{username}` | Telegram OSINT check |
| `/graph` | Relationship graph data |
| `/` | System status |

---

## 🎮 Frontend Dashboard (React)

- 🔥 Cyber SOC-style UI (dark mode)
- 📊 Real-time intelligence output viewer
- 🧠 Full scan / email / telegram panels
- ⚡ Live API integration with FastAPI backend

---

## 📦 Installation
```bash
git clone https://github.com/SentraSecurity/OSINT-SEARCHER.git
```
```bash
python -m venv venv
```
```bash
python3 -m venv venv
```
```bash
pip install -r requements.txt
```
```bash
python3 OSINT.py
```

## FRONTEND INSTALL

```bash
npm install
npm install react react-dom
```
```bash
npm create vite@latest osint-ui
cd osint-ui
npm install
npm run dev
```
Frontend Setup (React)
Create project:
```bash
npm create vite@latest osint-ui
cd osint-ui
npm install
npm run dev
```
🔗 Configuration
Inside frontend code:
```bash
const API = "http://localhost:8000";
```
🧪 Usage
🔎 Full Scan
```bash
http://localhost:8000/scan/target
```
📧 Email Scan
```bash
http://localhost:8000/email/test@gmail.com
```
📱 Telegram Scan
```bash
http://localhost:8000/telegram/username
```
🕸 System Architecture
```bash
Frontend (React Dashboard)
        ↓
FastAPI Backend (OSINT Engine)
        ↓
------------------------------
| Modules Layer              |
| - Social Scanner           |
| - IP Intelligence          |
| - Domain + DNS Recon       |
| - Email Breach Checker     |
| - Telegram OSINT Module    |
------------------------------
        ↓
SQLite Database
        ↓
Graph Intelligence Engine
```

### FRONTEND

```bash

import { useState } from "react"; import { Card, CardContent } from "@/components/ui/card"; import { Button } from "@/components/ui/button"; import { Input } from "@/components/ui/input"; import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function OSINTDashboard() { const [target, setTarget] = useState(""); const [email, setEmail] = useState(""); const [telegram, setTelegram] = useState(""); const [result, setResult] = useState(null);

const API = "http://localhost:8000";

const fetchScan = async () => { const res = await fetch(${API}/scan/${target}); setResult(await res.json()); };

const fetchEmail = async () => { const res = await fetch(${API}/email/${email}); setResult(await res.json()); };

const fetchTelegram = async () => { const res = await fetch(${API}/telegram/${telegram}); setResult(await res.json()); };

return ( <div className="p-6 grid gap-4 bg-black text-white min-h-screen"> <h1 className="text-3xl font-bold">🔥 OSINT GOD MODE DASHBOARD</h1>

<Tabs defaultValue="scan">
    <TabsList>
      <TabsTrigger value="scan">Full Scan</TabsTrigger>
      <TabsTrigger value="email">Email</TabsTrigger>
      <TabsTrigger value="telegram">Telegram</TabsTrigger>
    </TabsList>

    {/* FULL SCAN */}
    <TabsContent value="scan">
      <Card>
        <CardContent className="p-4 space-y-2">
          <Input placeholder="Target (username/domain/IP)" value={target} onChange={(e) => setTarget(e.target.value)} />
          <Button onClick={fetchScan}>Run Full Scan</Button>
        </CardContent>
      </Card>
    </TabsContent>

    {/* EMAIL */}
    <TabsContent value="email">
      <Card>
        <CardContent className="p-4 space-y-2">
          <Input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Button onClick={fetchEmail}>Scan Email</Button>
        </CardContent>
      </Card>
    </TabsContent>

    {/* TELEGRAM */}
    <TabsContent value="telegram">
      <Card>
        <CardContent className="p-4 space-y-2">
          <Input placeholder="Telegram username" value={telegram} onChange={(e) => setTelegram(e.target.value)} />
          <Button onClick={fetchTelegram}>Scan Telegram</Button>
        </CardContent>
      </Card>
    </TabsContent>
  </Tabs>

  {/* RESULT PANEL */}
  <Card className="bg-zinc-900">
    <CardContent className="p-4">
      <h2 className="text-xl mb-2">📊 Intelligence Output</h2>
      <pre className="text-xs overflow-auto max-h-[400px]">
        {result ? JSON.stringify(result, null, 2) : "No data yet"}
      </pre>
    </CardContent>
  </Card>
</div>

); }
