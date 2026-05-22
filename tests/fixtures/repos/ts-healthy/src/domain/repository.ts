// Domain-owned port. Infra implements it; domain never imports infra.

import type { Order } from "./order.js";

export interface OrderRepository {
  save(order: Order): Promise<void>;
  byId(id: string): Promise<Order | undefined>;
}
