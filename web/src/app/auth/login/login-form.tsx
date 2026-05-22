"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function LoginForm() {
  const searchParams = useSearchParams();
  const next = searchParams.get("next") ?? "/";
  const authError = searchParams.get("error");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(
    authError ? "로그인에 실패했습니다. 다시 시도해 주세요." : null,
  );
  const [loading, setLoading] = useState(false);

  const supabase = createClient();

  const redirectTo = () => {
    const origin = typeof window !== "undefined" ? window.location.origin : "";
    return `${origin}/auth/callback?next=${encodeURIComponent(next)}`;
  };

  const signInWithPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    const { error: signInError } = await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (signInError) {
      setError(signInError.message);
      return;
    }
    window.location.href = next;
  };

  const signInWithMagicLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    const { error: otpError } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: redirectTo() },
    });
    setLoading(false);
    if (otpError) {
      setError(otpError.message);
      return;
    }
    setMessage("이메일로 로그인 링크를 보냈습니다. 받은편지함을 확인해 주세요.");
  };

  const signUpWithPassword = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    const { error: signUpError } = await supabase.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: redirectTo() },
    });
    setLoading(false);
    if (signUpError) {
      setError(signUpError.message);
      return;
    }
    setMessage("가입 확인 메일을 보냈습니다. 이메일을 확인한 뒤 로그인해 주세요.");
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Jarvis 로그인</CardTitle>
          <CardDescription>이메일 매직 링크 또는 비밀번호로 로그인합니다.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {error && (
            <Alert variant="destructive">
              <AlertTitle>오류</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {message && (
            <Alert>
              <AlertTitle>안내</AlertTitle>
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}

          <Tabs defaultValue="magic">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="magic">매직 링크</TabsTrigger>
              <TabsTrigger value="password">비밀번호</TabsTrigger>
            </TabsList>

            <TabsContent value="magic">
              <form onSubmit={signInWithMagicLink} className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="email-magic">이메일</Label>
                  <Input
                    id="email-magic"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                  />
                </div>
                <Button type="submit" disabled={loading}>
                  로그인 링크 보내기
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="password">
              <form onSubmit={signInWithPassword} className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="email-pw">이메일</Label>
                  <Input
                    id="email-pw"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="password">비밀번호</Label>
                  <Input
                    id="password"
                    type="password"
                    required
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <Button type="submit" disabled={loading}>
                  로그인
                </Button>
                <Button type="button" variant="outline" disabled={loading} onClick={signUpWithPassword}>
                  계정 만들기
                </Button>
              </form>
            </TabsContent>
          </Tabs>

          <p className="text-muted-foreground text-center text-xs">
            <Link href="/" className="underline">
              대시보드로 돌아가기
            </Link>{" "}
            (로그인 필요)
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
