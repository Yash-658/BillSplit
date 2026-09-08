import type { Bill } from "../types";

export const mockBill: Bill = {
  restaurantName: "Demo Kitchen",
  currency: "INR",
  items: [
    { id: "biryani", name: "Chicken Biryani", quantity: 2, unitPrice: 35000, totalPrice: 70000, confidence: null },
    { id: "naan", name: "Garlic Naan (shared)", quantity: 2, unitPrice: 12000, totalPrice: 24000, confidence: null },
    { id: "paneer", name: "Paneer Tikka", quantity: 1, unitPrice: 46000, totalPrice: 46000, confidence: null },
    { id: "coke", name: "Coke", quantity: 2, unitPrice: 8000, totalPrice: 16000, confidence: null },
  ],
  subtotal: 156000,
  discount: 6000,
  serviceCharge: 12000,
  taxes: [28100],
  adjustment: null,
  printedTotal: 190100,
  confidence: { subtotal: null, discount: null, serviceCharge: null, taxes: [], printedTotal: null },
};
