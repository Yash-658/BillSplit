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
