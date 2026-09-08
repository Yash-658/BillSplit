import { ArrowLeft, RotateCcw, Sparkles } from "lucide-react";
import type { Assignment, Bill } from "../types";

const money = (value: number) => `₹${(value / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;

type PersonResult = { subtotal: number; discount: number; serviceCharge: number; tax: number; total: number; items: { name: string; share: number }[] };

function calculateResults(bill: Bill, people: string[], assignments: Assignment): Record<string, PersonResult> {
  const results: Record<string, PersonResult> = Object.fromEntries(people.map((person) => [person, { subtotal: 0, discount: 0, serviceCharge: 0, tax: 0, total: 0, items: [] }]));
  bill.items.forEach((item) => { const assigned = assignments[item.id] ?? []; const names = assigned.includes("everyone") ? people : assigned; const totalPrice = item.totalPrice ?? 0; const share = names.length ? Math.floor(totalPrice / names.length) : 0; names.forEach((name, index) => { const amount = index === names.length - 1 ? totalPrice - share * (names.length - 1) : share; results[name].subtotal += amount; results[name].items.push({ name: item.name ?? "Unnamed item", share: amount }); }); });
  const consumption = people.reduce((sum, person) => sum + results[person].subtotal, 0);
  const discount = bill.discount ?? 0;
  const serviceCharge = bill.serviceCharge ?? 0;
  const tax = bill.taxes.reduce((sum, value) => sum + value, 0);
  people.forEach((person) => { const ratio = consumption ? results[person].subtotal / consumption : 0; results[person].discount = Math.round(discount * ratio); results[person].serviceCharge = Math.round(serviceCharge * ratio); results[person].tax = Math.round(tax * ratio); results[person].total = results[person].subtotal - results[person].discount + results[person].serviceCharge + results[person].tax; });
  return results;
}

export function ResultsScreen({ bill, people, assignments, onBack, onStartOver }: { bill: Bill; people: string[]; assignments: Assignment; onBack: () => void; onStartOver: () => void }) {
  const results = calculateResults(bill, people, assignments);
  const allocated = people.reduce((sum, person) => sum + results[person].total, 0);
  const total = (bill.subtotal ?? 0) - (bill.discount ?? 0) + (bill.serviceCharge ?? 0) + bill.taxes.reduce((sum, value) => sum + value, 0) + (bill.adjustment ?? 0);
  return (
    <section><div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="mb-2 text-sm font-bold uppercase tracking-[0.18em] text-coral">Step 4 · Results</p><h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Everyone&apos;s share</h1><p className="mt-2 text-slate-500">A clear breakdown of what each person owes.</p></div><div className="flex items-center gap-2 text-sm font-semibold text-emerald-700"><Sparkles size={17} /> Ready to settle</div></div>
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">{people.map((person) => { const result = results[person]; return <article className="panel overflow-hidden" key={person}><div className="bg-ink p-5 text-white"><p className="text-sm text-slate-300">{person} owes</p><p className="mt-1 text-4xl font-bold">{money(result.total)}</p></div><div className="space-y-4 p-5"><div className="space-y-2 text-sm">{result.items.map((item) => <div className="flex justify-between gap-3" key={`${person}-${item.name}`}><span className="text-slate-600">{item.name}</span><span className="font-semibold">{money(item.share)}</span></div>)}</div><div className="border-t border-slate-100 pt-4 text-sm text-slate-500"><div className="flex justify-between"><span>Subtotal</span><span>{money(result.subtotal)}</span></div><div className="mt-2 flex justify-between"><span>Discount</span><span className="text-emerald-700">−{money(result.discount)}</span></div><div className="mt-2 flex justify-between"><span>Service charge</span><span>{money(result.serviceCharge)}</span></div><div className="mt-2 flex justify-between"><span>Tax</span><span>{money(result.tax)}</span></div></div></div></article>; })}</div>
      <div className="panel mt-6 p-5 sm:p-7"><div className="mb-5 flex items-center justify-between"><div><p className="text-sm font-semibold text-slate-500">Reconciliation</p><h2 className="mt-1 text-xl font-bold">The numbers add up</h2></div><span className={`rounded-full px-3 py-1 text-sm font-bold ${total === allocated ? "bg-mint text-emerald-700" : "bg-amber-100 text-amber-800"}`}>Difference {money(allocated - total)}</span></div><div className="grid gap-4 text-sm sm:grid-cols-3"><div className="rounded-xl bg-slate-50 p-4"><p className="text-slate-500">Overall bill total</p><p className="mt-1 text-xl font-bold">{money(total)}</p></div><div className="rounded-xl bg-slate-50 p-4"><p className="text-slate-500">Allocated total</p><p className="mt-1 text-xl font-bold">{money(allocated)}</p></div><div className="rounded-xl bg-slate-50 p-4"><p className="text-slate-500">People</p><p className="mt-1 text-xl font-bold">{people.length}</p></div></div></div>
      <div className="mt-6 flex flex-col-reverse justify-between gap-3 sm:flex-row"><button type="button" onClick={onBack} className="button-secondary"><ArrowLeft size={17} /> Back to assignment</button><button type="button" onClick={onStartOver} className="button-primary"><RotateCcw size={17} /> Start over</button></div>
    </section>
  );
}
