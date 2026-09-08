import { Receipt } from "lucide-react";
import type { ReactNode } from "react";
import type { Stage } from "../types";
import { Progress } from "./Progress";

export function Layout({ stage, children }: { stage: Stage; children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200/70 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5 sm:px-8">
          <div className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-coral text-white"><Receipt size={19} /></span>
            <span className="text-lg font-bold tracking-tight">Bill<span className="text-coral">Split</span></span>
          </div>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">Demo mode</span>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-5 py-8 sm:px-8 sm:py-12">
        <Progress current={stage} />
        {children}
      </main>
    </div>
  );
}
