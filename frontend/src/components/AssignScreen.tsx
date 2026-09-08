import { ArrowLeft, ArrowRight, Plus, Users, X } from "lucide-react";
import { useState } from "react";
import { calculateBill } from "../api";
import type { Assignment, Bill } from "../types";

export function AssignScreen({ bill, people, setPeople, assignments, setAssignments, onBack, onContinue }: { bill: Bill; people: string[]; setPeople: (people: string[]) => void; assignments: Assignment; setAssignments: (assignments: Assignment) => void; onBack: () => void; onContinue: (result: Awaited<ReturnType<typeof calculateBill>>) => void }) {
  const [newPerson, setNewPerson] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const addPerson = () => { const name = newPerson.trim(); if (people.length < 7 && name && !people.includes(name)) { setPeople([...people, name]); setNewPerson(""); } };
  const toggle = (itemId: string, person: string) => {
    const current = assignments[itemId] ?? [];
    const next = current.includes(person) ? current.filter((name) => name !== person) : [...current.filter((name) => name !== "everyone"), person];
    setAssignments({ ...assignments, [itemId]: next });
  };
  const everyone = (itemId: string) => setAssignments({ ...assignments, [itemId]: ["everyone"] });
  async function calculate() {
    if (loading || people.length < 2 || people.length > 7 || bill.items.some((item) => !(assignments[item.id]?.length))) return;
    setLoading(true);
    setError(null);
    try {
      onContinue(await calculateBill(bill, people, assignments));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Calculation failed.");
    } finally {
      setLoading(false);
    }
  }
  return (
    <section>
      <div className="mb-8"><p className="mb-2 text-sm font-bold uppercase tracking-[0.18em] text-coral">Step 3 · Assign</p><h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Who had what?</h1><p className="mt-2 text-slate-500">Select one or more people for each item. Shared dishes are split equally in this demo.</p></div>
      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <aside className="panel h-fit p-5"><div className="mb-4 flex items-center gap-2 font-bold"><Users size={18} /> People <span className="text-xs font-normal text-slate-500">({people.length}/7)</span></div><div className="space-y-2">{people.map((person) => <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm" key={person}><span>{person}</span><button type="button" onClick={() => setPeople(people.filter((name) => name !== person))} aria-label={`Remove ${person}`} className="text-slate-400 hover:text-coral"><X size={15} /></button></div>)}</div><div className="mt-5 flex gap-2"><input className="input" disabled={people.length >= 7} value={newPerson} onChange={(event) => setNewPerson(event.target.value)} onKeyDown={(event) => event.key === "Enter" && addPerson()} placeholder={people.length >= 7 ? "Maximum 7 people" : "Add person"} /><button type="button" disabled={people.length >= 7} onClick={addPerson} aria-label="Add person" className="rounded-lg bg-ink px-3 text-white disabled:cursor-not-allowed disabled:opacity-50"><Plus size={17} /></button></div>{people.length < 2 && <p className="mt-3 text-xs font-medium text-amber-700">Add at least 2 people to continue.</p>}</aside>
        <div className="panel divide-y divide-slate-100">{bill.items.map((item) => { const selected = assignments[item.id] ?? []; const shared = selected.length > 1 || selected.includes("everyone"); return <div className="p-5" key={item.id}><div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="font-bold">{item.name ?? "Unnamed item"}</h2><p className="mt-1 text-sm text-slate-500">₹{((item.totalPrice ?? 0) / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })} · {item.quantity ?? "—"} item{item.quantity === 1 ? "" : "s"}</p></div>{shared && <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-orange-700">Shared</span>}</div><div className="flex flex-wrap gap-2">{people.map((person) => <button type="button" key={person} onClick={() => toggle(item.id, person)} className={`rounded-lg border px-3 py-2 text-sm font-semibold transition ${selected.includes(person) ? "border-ink bg-ink text-white" : "border-slate-200 text-slate-600 hover:border-slate-300"}`}>{person}</button>)}<button type="button" onClick={() => everyone(item.id)} className={`rounded-lg border px-3 py-2 text-sm font-semibold transition ${selected.includes("everyone") ? "border-coral bg-coral text-white" : "border-slate-200 text-slate-600 hover:border-coral"}`}>Everyone</button></div>{selected.length === 0 && <p className="mt-3 text-xs font-medium text-amber-700">Choose at least one person.</p>}</div> })}{error && <div className="mx-5 rounded-xl bg-red-50 p-4 text-sm text-red-800" role="alert">{error}</div>}<div className="flex flex-col-reverse justify-between gap-3 p-5 sm:flex-row"><button type="button" onClick={onBack} className="button-secondary"><ArrowLeft size={17} /> Back</button><button type="button" disabled={loading || people.length < 2 || people.length > 7 || bill.items.some((item) => !(assignments[item.id]?.length))} onClick={calculate} className="button-primary disabled:cursor-not-allowed disabled:opacity-50">{loading ? "Calculating..." : <>See results <ArrowRight size={17} /></>}</button></div></div>
      </div>
    </section>
  );
}
