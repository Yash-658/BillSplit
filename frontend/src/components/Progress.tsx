import { Check } from "lucide-react";
import type { Stage } from "../types";

const stages: { key: Stage; label: string }[] = [
  { key: "upload", label: "Upload" },
  { key: "review", label: "Review" },
  { key: "assign", label: "Assign" },
  { key: "results", label: "Results" },
];

export function Progress({ current }: { current: Stage }) {
  const activeIndex = stages.findIndex((stage) => stage.key === current);
  return (
    <nav aria-label="Progress" className="mb-10 flex items-center justify-center gap-2 sm:gap-4">
      {stages.map((stage, index) => (
        <div className="flex items-center gap-2 sm:gap-4" key={stage.key}>
          <div className={`flex items-center gap-2 text-xs font-semibold sm:text-sm ${index <= activeIndex ? "text-ink" : "text-slate-400"}`}>
            <span className={`flex h-8 w-8 items-center justify-center rounded-full ${index < activeIndex ? "bg-mint text-emerald-700" : index === activeIndex ? "bg-ink text-white" : "bg-slate-100 text-slate-400"}`}>
              {index < activeIndex ? <Check size={15} /> : index + 1}
            </span>
            <span className="hidden sm:inline">{stage.label}</span>
          </div>
          {index < stages.length - 1 && <span className="h-px w-5 bg-slate-200 sm:w-12" />}
        </div>
      ))}
    </nav>
  );
}
