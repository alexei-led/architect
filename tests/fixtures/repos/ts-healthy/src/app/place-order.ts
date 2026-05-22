// Use-case. Depends on domain only.

import type { Order } from "../domain/order.js";
import { orderTotal } from "../domain/order.js";
import type { OrderRepository } from "../domain/repository.js";

export async function placeOrder(repo: OrderRepository, order: Order): Promise<number> {
  await repo.save(order);
  return orderTotal(order);
}
