// Domain type — but it imports the gateway, creating a cycle (order <-> gateway).
import { notifyPlaced } from "./gateway.js";

export interface Order {
  id: string;
  lines: ReadonlyArray<{ sku: string; qty: number; unitPrice: number }>;
}

// Private internal. Not exported as a stable interface.
function _applyTax(subtotal: number): number {
  return subtotal * 1.2;
}

export function orderTotal(order: Order): number {
  const subtotal = order.lines.reduce((sum, l) => sum + l.qty * l.unitPrice, 0);
  return _applyTax(subtotal);
}

export function place(order: Order): number {
  const total = orderTotal(order);
  notifyPlaced(order.id); // domain reaching out to the gateway closes the cycle
  return total;
}

// Re-exported so the gateway can reach into the private tax rule.
export { _applyTax };
