// Adapter. Implements a domain port. Never imported by domain or app internals.

import type { Order } from "../domain/order.js";
import type { OrderRepository } from "../domain/repository.js";

export class MemoryOrderRepository implements OrderRepository {
  private readonly store = new Map<string, Order>();

  async save(order: Order): Promise<void> {
    this.store.set(order.id, order);
  }

  async byId(id: string): Promise<Order | undefined> {
    return this.store.get(id);
  }
}
