// Pure domain. No imports from app or infra.

export interface Order {
  id: string;
  lines: ReadonlyArray<{ sku: string; qty: number; unitPrice: number }>;
}

export function orderTotal(order: Order): number {
  return order.lines.reduce((sum, l) => sum + l.qty * l.unitPrice, 0);
}
