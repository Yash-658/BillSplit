export type Stage = "upload" | "review" | "assign" | "results";

export type BillItem = {
  id: string;
  name: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
};

export type Bill = {
  items: BillItem[];
  subtotal: number;
  discount: number;
  serviceCharge: number;
  tax: number;
  printedTotal: number;
};

export type Assignment = Record<string, string[]>;
