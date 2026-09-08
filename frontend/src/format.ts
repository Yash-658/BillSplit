export function formatPaise(value: number): string {
  return `₹${(value / 100).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatValidationMessage(message: string): string {
  return message.replace(/(-?\d+) paise\b/g, (_, value: string) => formatPaise(Number(value)));
}
