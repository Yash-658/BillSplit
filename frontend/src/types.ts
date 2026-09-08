export type Stage = "upload" | "review" | "assign" | "results";

export type BillItem = {
  id: string;
  name: string | null;
  quantity: number | null;
  unitPrice: number | null;
  totalPrice: number | null;
  confidence: number | null;
};

export type Bill = {
  restaurantName: string | null;
  currency: string | null;
  items: BillItem[];
  subtotal: number | null;
  discount: number | null;
  serviceCharge: number | null;
  taxes: number[];
  adjustment: number | null;
  printedTotal: number | null;
  confidence: {
    subtotal: number | null;
    discount: number | null;
    serviceCharge: number | null;
    taxes: number[];
    printedTotal: number | null;
  };
};

export type Assignment = Record<string, string[]>;

export type PersonBreakdown = {
  item_shares: Record<string, number>;
  subtotal: number;
  discount: number;
  service_charge: number;
  tax: number;
  total: number;
};

export type CalculateResult = {
  people: Record<string, PersonBreakdown>;
  bill_total: number;
  allocated_total: number;
  difference: number;
  validation: {
    status: string;
    calculated_total: number | null;
    printed_total: number | null;
    difference: number | null;
    messages: string[];
  };
};
