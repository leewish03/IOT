"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { User } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function UserMenu() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const supabase = createClient();

    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signOut = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/auth/login");
    router.refresh();
  };

  if (loading) {
    return <Badge variant="secondary">세션 확인 중…</Badge>;
  }

  if (!user) {
    return (
      <Button variant="outline" size="sm" onClick={() => router.push("/auth/login")}>
        로그인
      </Button>
    );
  }

  const label = user.email ?? user.id.slice(0, 8);

  return (
    <div className="flex items-center gap-2">
      <Badge variant="secondary" className="max-w-[200px] truncate font-normal">
        {label}
      </Badge>
      <Button variant="outline" size="sm" onClick={signOut}>
        로그아웃
      </Button>
    </div>
  );
}
