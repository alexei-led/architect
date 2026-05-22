// "Infra" gateway that also owns persistence and tax math: a god module.
// It imports a private domain internal (_applyTax) instead of a published API,
// and order.ts imports back from here — a two-node cycle.
import type { Order } from "./order.js";
import { _applyTax } from "./order.js";

const store = new Map<string, Order>();

export function notifyPlaced(id: string): void {
  // pretend transport
  void id;
}

export function persist(order: Order): void {
  store.set(order.id, order);
}

// Reaches into the domain's private tax rule rather than calling orderTotal.
export function quote(subtotal: number): number {
  return _applyTax(subtotal);
}
