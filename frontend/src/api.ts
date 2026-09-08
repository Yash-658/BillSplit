import type { Bill } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type ExtractedNumericField = { value: number | null; confidence: number };
type ExtractedItem = {
  id: string | null;
  name: string | null;
  quantity: number | null;
  unit_price: ExtractedNumericField | null;
  total_price: ExtractedNumericField | null;
  confidence: number;
};
type BillExtraction = {
  restaurant_name: string | null;
  currency: string | null;
  items: ExtractedItem[];
  subtotal: ExtractedNumericField | null;
  discount: ExtractedNumericField | null;
  service_charge: ExtractedNumericField | null;
  taxes: ExtractedNumericField[];
  adjustment: number | null;
  printed_total: ExtractedNumericField | null;
};

const valueOf = (field: ExtractedNumericField | null) => field?.value ?? null;

export async function extractBill(files: File[]): Promise<Bill> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const response = await fetch(`${API_BASE_URL}/extract`, { method: "POST", body: formData });
  if (!response.ok) {
    let detail = "Bill extraction failed.";
    try {
      const body = await response.json() as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // Keep the user-facing fallback for non-JSON or unavailable responses.
    }
    throw new Error(detail);
  }
  const extraction = await response.json() as BillExtraction;
  return {
    restaurantName: extraction.restaurant_name,
    currency: extraction.currency,
    items: extraction.items.map((item, index) => ({
      id: item.id ?? `extracted-item-${index}`,
      name: item.name,
      quantity: item.quantity,
      unitPrice: valueOf(item.unit_price),
      totalPrice: valueOf(item.total_price),
      confidence: item.confidence,
    })),
    subtotal: valueOf(extraction.subtotal),
    discount: valueOf(extraction.discount),
    serviceCharge: valueOf(extraction.service_charge),
    taxes: extraction.taxes.map((tax) => tax.value).filter((value): value is number => value !== null),
    adjustment: extraction.adjustment,
    printedTotal: valueOf(extraction.printed_total),
    confidence: {
      subtotal: extraction.subtotal?.confidence ?? null,
      discount: extraction.discount?.confidence ?? null,
      serviceCharge: extraction.service_charge?.confidence ?? null,
      taxes: extraction.taxes.map((tax) => tax.confidence),
      printedTotal: extraction.printed_total?.confidence ?? null,
    },
  };
}
