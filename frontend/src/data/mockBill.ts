import type { Bill } from "../types";

export const mockBill: Bill = {
  items: [
    { id: "biryani", name: "Chicken Biryani", quantity: 2, unitPrice: 350, totalPrice: 700 },
    { id: "naan", name: "Garlic Naan (shared)", quantity: 2, unitPrice: 120, totalPrice: 240 },
    { id: "paneer", name: "Paneer Tikka", quantity: 1, unitPrice: 460, totalPrice: 460 },
    { id: "coke", name: "Coke", quantity: 2, unitPrice: 80, totalPrice: 160 },
  ],
  subtotal: 1560,
  discount: 60,
  serviceCharge: 120,
  tax: 281,
  printedTotal: 1901,
};
