from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from marketplace_core import (Capability, DomainError, IdempotencyConflict,
    InvalidTransition, MarketplaceEngine, Money, NotFound, OrderStatus, PermissionDenied)


class Clock:
    def __init__(self): self.value = datetime(2026, 11, 23, 12, tzinfo=timezone.utc)
    def __call__(self): return self.value
    def tick(self): self.value += timedelta(seconds=1)


class MarketplaceTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.engine = MarketplaceEngine(self.clock)
        self.capability = Capability("cap.design.v1", "org.seller", 1, "Product Design",
            "Create a validated product specification.", ("brief",), ("spec",), ("read:brief",))
        self.engine.register_capability(self.capability)
        self.listing = self.engine.create_listing(listing_id="listing.design.v1", owner_org_id="org.seller",
            capability_id="cap.design.v1", version=1, title="Design sprint", description="Scoped sprint",
            price=Money(Decimal("499.00"), "USD"), acceptance_criteria=("file delivered", "buyer accepts"))

    def publish(self): return self.engine.publish_listing(self.listing.listing_id)
    def order(self, key="request-1"):
        self.publish()
        return self.engine.create_order(buyer_org_id="org.buyer", listing_id=self.listing.listing_id, idempotency_key=key)

    def test_money_is_decimal_safe(self):
        self.assertEqual(Money("499.00", "USD").amount, Decimal("499.00"))
        for args in [(2.5, "USD"), (Decimal("-1"), "USD"), (Decimal("NaN"), "USD"), (1, "usd")]:
            with self.assertRaises(DomainError): Money(*args)

    def test_capability_owner_and_duplicate_are_enforced(self):
        with self.assertRaises(PermissionDenied):
            self.engine.create_listing(listing_id="wrong", owner_org_id="org.other", capability_id="cap.design.v1",
                version=1, title="x", description="x", price=Money(1, "USD"), acceptance_criteria=("ok",))
        with self.assertRaises(DomainError): self.engine.register_capability(self.capability)
        with self.assertRaises(NotFound):
            self.engine.create_listing(listing_id="missing", owner_org_id="org.seller", capability_id="missing",
                version=1, title="x", description="x", price=Money(1, "USD"), acceptance_criteria=("ok",))

    def test_draft_and_suspended_listing_cannot_be_ordered(self):
        with self.assertRaises(DomainError): self.engine.create_order(buyer_org_id="org.buyer",
            listing_id=self.listing.listing_id, idempotency_key="a")
        self.publish(); self.engine.suspend_listing(self.listing.listing_id)
        with self.assertRaises(DomainError): self.engine.create_order(buyer_org_id="org.buyer",
            listing_id=self.listing.listing_id, idempotency_key="b")

    def test_self_purchase_is_rejected(self):
        self.publish()
        with self.assertRaises(DomainError): self.engine.create_order(buyer_org_id="org.seller",
            listing_id=self.listing.listing_id, idempotency_key="c")

    def test_order_snapshot_and_idempotent_retry(self):
        first = self.order()
        retry = self.engine.create_order(buyer_org_id="org.buyer", listing_id=self.listing.listing_id,
            idempotency_key="request-1")
        self.assertEqual(first.order_id, retry.order_id)
        self.assertEqual(first.price_snapshot, Money(Decimal("499.00"), "USD"))
        self.assertEqual(first.listing_version, 1)
        self.assertEqual(first.acceptance_criteria_snapshot, self.listing.acceptance_criteria)
        self.assertEqual(len(self.engine.list_orders()), 1)

    def test_idempotency_key_cannot_be_reused_for_another_request(self):
        self.order()
        with self.assertRaises(IdempotencyConflict): self.engine.create_order(buyer_org_id="org.other",
            listing_id=self.listing.listing_id, idempotency_key="request-1")

    def test_order_lifecycle_and_party_permissions(self):
        order = self.order()
        with self.assertRaises(PermissionDenied): self.engine.transition_order(order_id=order.order_id,
            actor_org_id="org.buyer", target_status=OrderStatus.ACCEPTED, reason="wrong actor")
        for actor, status in [("org.seller", OrderStatus.ACCEPTED), ("org.seller", OrderStatus.IN_PROGRESS),
                              ("org.seller", OrderStatus.DELIVERED), ("org.buyer", OrderStatus.ACCEPTED_BY_BUYER)]:
            self.clock.tick()
            order = self.engine.transition_order(order_id=order.order_id, actor_org_id=actor,
                target_status=status, reason="transition test")
        self.assertEqual(order.status, OrderStatus.ACCEPTED_BY_BUYER)
        self.assertEqual(len(order.history), 5)

    def test_terminal_order_cannot_be_reopened_and_non_party_cannot_cancel(self):
        order = self.order("request-2")
        with self.assertRaises(PermissionDenied): self.engine.transition_order(order_id=order.order_id,
            actor_org_id="org.stranger", target_status=OrderStatus.CANCELLED, reason="not a party")
        order = self.engine.transition_order(order_id=order.order_id, actor_org_id="org.seller",
            target_status=OrderStatus.REJECTED, reason="capacity unavailable")
        with self.assertRaises(InvalidTransition): self.engine.transition_order(order_id=order.order_id,
            actor_org_id="org.seller", target_status=OrderStatus.ACCEPTED, reason="reopen")

    def test_clock_must_be_timezone_aware(self):
        bad = MarketplaceEngine(lambda: datetime(2026, 11, 23, 12))
        bad.register_capability(self.capability)
        listing = bad.create_listing(listing_id="naive", owner_org_id="org.seller", capability_id="cap.design.v1",
            version=1, title="x", description="x", price=Money(0, "USD"), acceptance_criteria=("ok",))
        bad.publish_listing(listing.listing_id)
        with self.assertRaises(DomainError): bad.create_order(buyer_org_id="org.buyer",
            listing_id=listing.listing_id, idempotency_key="naive-clock")


if __name__ == "__main__": unittest.main(verbosity=2)
