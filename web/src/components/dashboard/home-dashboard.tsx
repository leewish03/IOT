"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { MODEL_CATALOG_AS_OF, MODEL_OPTIONS, type ModelKey } from "@/lib/models";
import { UserMenu } from "@/components/auth/user-menu";

type ChatLine = { role: "user" | "assistant"; content: string };

async function callOrchestrator(tool: string, args: Record<string, unknown>) {
  const res = await fetch("/api/orchestrator/tool", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool, args }),
  });
  return res.json();
}

export function HomeDashboard() {
  const [model, setModel] = useState<ModelKey>("claude-haiku-4.6");
  const [health, setHealth] = useState<string>("checking");
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null);
  const [chat, setChat] = useState<ChatLine[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoVision, setAutoVision] = useState(false);
  const [visionResult, setVisionResult] = useState<string>("");
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const refreshStatus = useCallback(async () => {
    try {
      const h = await fetch("/api/orchestrator/tool?action=health");
      const hj = await h.json();
      setHealth(hj.status === "ok" ? "online" : "degraded");
      const s = await callOrchestrator("system.status_summary", {});
      if (s.success) setSummary(s.data);
    } catch {
      setHealth("offline");
    }
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  const sendChat = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    const userMsg = input.trim();
    setInput("");
    setChat((c) => [...c, { role: "user", content: userMsg }]);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, model, history: chat }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "chat failed");
      setChat((c) => [...c, { role: "assistant", content: data.reply }]);
      await refreshStatus();
    } catch (e) {
      setError(e instanceof Error ? e.message : "chat error");
    } finally {
      setLoading(false);
    }
  };

  const toggleRelay = async (channel: "ch1" | "ch2", on: boolean) => {
    setError(null);
    const tool = on ? "relay.turn_on" : "relay.turn_off";
    const result = await callOrchestrator(tool, { channel });
    if (!result.success) setError(result.error ?? "relay failed");
    await refreshStatus();
  };

  const startVoice = async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const form = new FormData();
        form.append("audio", blob);
        form.append("model", model);
        setLoading(true);
        const res = await fetch("/api/voice", { method: "POST", body: form });
        const data = await res.json();
        setLoading(false);
        if (!res.ok) throw new Error(data.error ?? "voice failed");
        setChat((c) => [
          ...c,
          { role: "user", content: `[음성] ${data.transcript}` },
          { role: "assistant", content: data.reply },
        ]);
        await refreshStatus();
        stream.getTracks().forEach((t) => t.stop());
      };
      mediaRef.current = recorder;
      recorder.start();
      setTimeout(() => recorder.stop(), 4000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "mic error");
    }
  };

  const onVisionFile = async (file: File | null) => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const form = new FormData();
    form.append("image", file);
    form.append("model", model);
    form.append("autoAct", String(autoVision));
    try {
      const res = await fetch("/api/vision", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "vision failed");
      setVisionResult(data.analysis + (data.reply ? `\n\n${data.reply}` : ""));
      await refreshStatus();
    } catch (e) {
      setError(e instanceof Error ? e.message : "vision error");
    } finally {
      setLoading(false);
    }
  };

  const env = summary?.environment as { temperature_c?: number; humidity_pct?: number } | undefined;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold tracking-tight">집 Jarvis 대시보드</h1>
          <p className="text-muted-foreground text-sm">
            Phase 0·3·4·5 — 수동 제어, 채팅, 음성(4초), 비전. 오케스트레이터:{" "}
            <Badge variant={health === "online" ? "default" : "destructive"}>{health}</Badge>
          </p>
        </div>
        <UserMenu />
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTitle>오류</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex flex-wrap items-center gap-4">
        <div className="flex flex-col gap-2">
          <Label>AI 모델 ({MODEL_CATALOG_AS_OF} 기준)</Label>
          <Select value={model} onValueChange={(v) => setModel(v as ModelKey)}>
            <SelectTrigger className="w-[280px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {MODEL_OPTIONS.map((m) => (
                <SelectItem key={m.key} value={m.key}>
                  {m.label} — {m.apiModel}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-muted-foreground max-w-md text-xs">
            {MODEL_OPTIONS.find((m) => m.key === model)?.catalogNote}
          </p>
        </div>
        <div className="flex items-center gap-2 pt-6">
          <Switch checked={autoVision} onCheckedChange={setAutoVision} id="auto-vision" />
          <Label htmlFor="auto-vision">비전 후 자동 도구 실행</Label>
        </div>
      </div>

      <Tabs defaultValue="control">
        <TabsList>
          <TabsTrigger value="control">수동 제어</TabsTrigger>
          <TabsTrigger value="chat">채팅 (Phase 3)</TabsTrigger>
          <TabsTrigger value="vision">비전 (Phase 4)</TabsTrigger>
        </TabsList>

        <TabsContent value="control" className="flex flex-col gap-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>릴레이</CardTitle>
                <CardDescription>즉시 on/off</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-2">
                <Button onClick={() => toggleRelay("ch1", true)}>CH1 ON</Button>
                <Button variant="outline" onClick={() => toggleRelay("ch1", false)}>
                  CH1 OFF
                </Button>
                <Button onClick={() => toggleRelay("ch2", true)}>CH2 ON</Button>
                <Button variant="outline" onClick={() => toggleRelay("ch2", false)}>
                  CH2 OFF
                </Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>환경 센서</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  온도 {env?.temperature_c ?? "—"}°C · 습도 {env?.humidity_pct ?? "—"}%
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>자동화</CardTitle>
              </CardHeader>
              <CardContent>
                <Button
                  className="w-full"
                  onClick={async () => {
                    const r = await callOrchestrator("automation.prepare_class_day", {
                      profile: "aggressive",
                    });
                    if (!r.success) setError(r.error);
                    else await refreshStatus();
                  }}
                >
                  수업일 알람 준비
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="chat" className="flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle>음성 · 채팅</CardTitle>
              <CardDescription>마이크 4초 녹음 후 STT → AI → 도구 호출</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <Button type="button" variant="secondary" onClick={startVoice} disabled={loading}>
                말하기 (4초)
              </Button>
              <ScrollArea className="h-48 rounded-md border p-3">
                {chat.length === 0 && (
                  <p className="text-muted-foreground text-sm">예: 거실 전등 켜줘, 내일 일정 알려줘</p>
                )}
                {chat.map((line, i) => (
                  <p key={i} className="mb-2 text-sm">
                    <strong>{line.role === "user" ? "나" : "AI"}:</strong> {line.content}
                  </p>
                ))}
              </ScrollArea>
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendChat()}
                  placeholder="명령을 입력하세요"
                />
                <Button onClick={sendChat} disabled={loading}>
                  전송
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vision">
          <Card>
            <CardHeader>
              <CardTitle>비전 분석</CardTitle>
              <CardDescription>사진 업로드 → 상황 판단 → (선택) 도구 실행</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <Input type="file" accept="image/*" onChange={(e) => onVisionFile(e.target.files?.[0] ?? null)} />
              {visionResult && <Textarea readOnly value={visionResult} rows={8} />}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
