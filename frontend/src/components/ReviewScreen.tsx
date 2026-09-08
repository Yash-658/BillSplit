import { ArrowRight, CheckCircle2, Info } from "lucide-react";
import type { Bill } from "../types";

const money = (value: number) => `₹${value.toLocaleString("en-IN")}`;

export function ReviewScreen({ bill, setBill, onContinue }: { bill: Bill; setBill: (bill: Bill) => void; onContinue: () => void }) {
  const itemTotal = bill.items.reduce((sum, item) => sum + item.totalPrice, 0);
  const calculated = bill.subtotal - bill.discount + bill.serviceCharge + bill.tax;
  const updateItem = (id: string, field: "quantity" | "unitPrice" | "totalPrice", value: number) => setBill({ ...bill, items: bill.items.map((item) => item.id === id ? { ...item, [field]: value } : item) });
  const updateBill = (field: keyof Bill, value: number) => setBill({ ...bill, [field]: value });
  const warning = calculated !== bill.printedTotal || itemTotal !== bill.subtotal;

  return (
    <section>
      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div><p className="mb-2 text-sm font-bold uppercase tracking-[0.18em] text-coral">Step 2 · Human verification</p><h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Review your bill</h1><p className="mt-2 text-slate-500">Check the extracted values and correct anything that looks off.</p></div>
        <div className="flex items-center gap-2 rounded-xl bg-mint px-3 py-2 text-sm font-semibold text-emerald-800"><CheckCircle2 size={17} /> You&apos;re in control</div>
      </div>
      <div className="panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[650px] text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500"><tr><th className="px-5 py-4 font-semibold">Item</th><th className="px-3 py-4 font-semibold">Qty</th><th className="px-3 py-4 font-semibold">Unit price</th><th className="px-3 py-4 font-semibold">Total</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {bill.items.map((item) => <tr key={item.id}><td className="px-5 py-4 font-medium">{item.name}</td><td className="px-3 py-4"><input className="input w-20" type="number" min="0" value={item.quantity} onChange={(event) => updateItem(item.id, "quantity", Number(event.target.value))} /></td><td className="px-3 py-4"><input className="input w-28" type="number" min="0" value={item.unitPrice} onChange={(event) => updateItem(item.id, "unitPrice", Number(event.target.value))} /></td><td className="px-3 py-4"><input className="input w-28" type="number" min="0" value={item.totalPrice} onChange={(event) => updateItem(item.id, "totalPrice", Number(event.target.value))} /></td></tr>)}
            </tbody>
          </table>
        </div>
        <div className="grid gap-4 border-t border-slate-100 p-5 sm:grid-cols-2 lg:grid-cols-4">
          {([["subtotal", "Subtotal"], ["discount", "Discount"], ["serviceCharge", "Service charge"], ["tax", "Tax"], ["printedTotal", "Printed total"]] as const).map(([field, label]) => <label className="text-sm font-semibold text-slate-600" key={field}>{label}<input className="input mt-2" type="number" min="0" value={bill[field]} onChange={(event) => updateBill(field, Number(event.target.value))} /></label>)}
        </div>
        <div className={`mx-5 mb-5 flex items-start gap-3 rounded-xl p-4 text-sm ${warning ? "bg-amber-50 text-amber-900" : "bg-mint text-emerald-800"}`}><Info size={18} className="mt-0.5 shrink-0" /><div><p className="font-bold">{warning ? "Review needed" : "Bill arithmetic looks good"}</p><p className="mt-1">{warning ? `Calculated total ${money(calculated)} does not match the reviewed values. You can continue after checking them.` : "Totals reconcile with the line items."}</p></div></div>
        <div className="flex justify-end border-t border-slate-100 p-5"><button type="button" onClick={onContinue} className="button-primary">Confirm Bill <ArrowRight size={17} /></button></div>
      </div>
    </section>
  );
}
