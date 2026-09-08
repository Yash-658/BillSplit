import type { Assignment, Bill, CalculateResult } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type ExtractedNumericField = { value: number | null; confidence: number };
type ExtractedTextField = { value: string | null; confidence: number };
type ExtractedItem = {
  id: string | null;
  name: ExtractedTextField;
  quantity: ExtractedNumericField;
  unit_price: ExtractedNumericField | null;
  total_price: ExtractedNumericField | null;
  confidence: number;
};
type BillExtraction = {
  restaurant_name: ExtractedTextField | null;
  currency: ExtractedTextField | null;
  items: ExtractedItem[];
  subtotal: ExtractedNumericField | null;
  discount: ExtractedNumericField | null;
  service_charge: ExtractedNumericField | null;
  taxes: ExtractedNumericField[];
  adjustment: ExtractedNumericField | null;
  printed_total: ExtractedNumericField | null;
};

const valueOf = (field: ExtractedNumericField | null) => field?.value ?? null;
const textValueOf = (field: ExtractedTextField | null) => field?.value ?? null;

export type ValidationResult = {
  status: string;
  calculated_total: number | null;
  printed_total: number | null;
  difference: number | null;
  messages: string[];
};

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
    restaurantName: textValueOf(extraction.restaurant_name),
    currency: textValueOf(extraction.currency),
    items: extraction.items.map((item, index) => ({
      id: item.id ?? `extracted-item-${index}`,
      name: item.name.value,
      quantity: item.quantity.value,
      unitPrice: valueOf(item.unit_price),
      totalPrice: valueOf(item.total_price),
      confidence: item.confidence,
      nameConfidence: item.name.confidence,
      quantityConfidence: item.quantity.confidence,
      unitPriceConfidence: item.unit_price?.confidence ?? null,
      totalPriceConfidence: item.total_price?.confidence ?? null,
    })),
    subtotal: valueOf(extraction.subtotal),
    discount: valueOf(extraction.discount),
    serviceCharge: valueOf(extraction.service_charge),
    taxes: extraction.taxes.map((tax) => tax.value).filter((value): value is number => value !== null),
    adjustment: valueOf(extraction.adjustment),
    printedTotal: valueOf(extraction.printed_total),
    confidence: {
      restaurantName: extraction.restaurant_name?.confidence ?? null,
      currency: extraction.currency?.confidence ?? null,
      subtotal: extraction.subtotal?.confidence ?? null,
      discount: extraction.discount?.confidence ?? null,
      serviceCharge: extraction.service_charge?.confidence ?? null,
      taxes: extraction.taxes.map((tax) => tax.confidence),
      adjustment: extraction.adjustment?.confidence ?? null,
      printedTotal: extraction.printed_total?.confidence ?? null,
    },
  };
}

export async function validateBill(bill: Bill): Promise<ValidationResult> {
  return requestJson<ValidationResult>("/validate", {
    items: toBillItems(bill),
    subtotal: bill.subtotal,
    discount: bill.discount,
    service_charge: bill.serviceCharge,
    tax: bill.taxes.reduce((sum, value) => sum + value, 0),
    adjustment: bill.adjustment,
    printed_total: bill.printedTotal,
  });
}

function toBillItems(bill: Bill) {
  return bill.items.map((item) => {
    if (item.name === null || item.quantity === null || item.unitPrice === null || item.totalPrice === null) {
      throw new Error("Complete each item's name, quantity, unit price, and total before confirming.");
    }
    return {
      id: item.id,
      name: item.name,
      quantity: item.quantity,
      unit_price: item.unitPrice,
      total_price: item.totalPrice,
    };
  });
}

async function requestJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    let detail = "Request failed.";
    try {
      const errorBody = await response.json() as { detail?: string | string[] };
      if (errorBody.detail) detail = Array.isArray(errorBody.detail) ? errorBody.detail.join(" ") : errorBody.detail;
    } catch {
      // Keep the user-facing fallback for non-JSON or unavailable responses.
    }
    throw new Error(detail);
  }
  return await response.json() as T;
}

export async function calculateBill(bill: Bill, people: string[], assignments: Assignment): Promise<CalculateResult> {
  return requestJson<CalculateResult>("/calculate", {
    bill: {
      items: toBillItems(bill),
      subtotal: bill.subtotal,
      discount: bill.discount,
      service_charge: bill.serviceCharge,
      tax: bill.taxes.reduce((sum, value) => sum + value, 0),
      adjustment: bill.adjustment,
      printed_total: bill.printedTotal,
    },
    people,
    assignments,
  });
}
