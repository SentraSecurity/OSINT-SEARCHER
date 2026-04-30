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
