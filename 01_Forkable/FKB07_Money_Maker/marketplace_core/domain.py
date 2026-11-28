"""A'Space Marketplace Day 1: in-memory capability, listing and order domain.

No persistence, authentication, payments, escrow, settlement, refunds, external
agent dispatch, API, or legal guarantee is implemented. Caller-supplied org IDs
must be authenticated by a future adapter before any live deployment.
"""
from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Callable, Iterable


class DomainError(ValueError):
    """A domain invariant was violated."""


class NotFound(DomainError):
    pass


class IdempotencyConflict(DomainError):
    pass


class InvalidTransition(DomainError):
    pass


class PermissionDenied(DomainError):
    pass


def _text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise DomainError(f"{field} must be a non-empty trimmed string")
    return value


def _texts(values: Iterable[str], field: str) -> tuple[str, ...]:
    result = tuple(_text(v, field) for v in values)
    if not result or len(set(result)) != len(result):
        raise DomainError(f"{field} must be non-empty and contain no duplicates")
    return result


def _now(clock: Callable[[], datetime]) -> datetime:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise DomainError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.amount, (bool, float)):
            raise DomainError("Money amount must be Decimal, int or decimal string; float is unsafe")
        try:
            value = self.amount if isinstance(self.amount, Decimal) else Decimal(str(self.amount))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise DomainError("invalid decimal amount") from exc
        if not value.is_finite() or value < 0:
            raise DomainError("Money amount must be finite and non-negative")
        if not isinstance(self.currency, str) or not re.fullmatch(r"[A-Z]{3}", self.currency):
            raise DomainError("currency must be a 3-letter uppercase code")
        object.__setattr__(self, "amount", value)


class ListingStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class OrderStatus(str, Enum):
    PLACED = "PLACED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    DELIVERED = "DELIVERED"
    ACCEPTED_BY_BUYER = "ACCEPTED_BY_BUYER"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


@dataclass(frozen=True, slots=True)
class Capability:
    capability_id: str
    owner_org_id: str
    version: int
    name: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    permissions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for key in ("capability_id", "owner_org_id", "name", "purpose"):
            _text(getattr(self, key), key)
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version < 1:
            raise DomainError("capability version must be a positive integer")
        object.__setattr__(self, "inputs", _texts(self.inputs, "inputs"))
        object.__setattr__(self, "outputs", _texts(self.outputs, "outputs"))
        object.__setattr__(self, "permissions", tuple(_text(x, "permissions") for x in self.permissions))


@dataclass(frozen=True, slots=True)
class Listing:
    listing_id: str
    owner_org_id: str
    capability_id: str
    capability_version: int
    version: int
    title: str
    description: str
    price: Money
    acceptance_criteria: tuple[str, ...]
    status: ListingStatus = ListingStatus.DRAFT

    def __post_init__(self) -> None:
        for key in ("listing_id", "owner_org_id", "capability_id", "title", "description"):
            _text(getattr(self, key), key)
        for key in ("version", "capability_version"):
            value = getattr(self, key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise DomainError(f"{key} must be a positive integer")
        if not isinstance(self.price, Money) or not isinstance(self.status, ListingStatus):
            raise DomainError("listing price or status has an invalid type")
        object.__setattr__(self, "acceptance_criteria", _texts(self.acceptance_criteria, "acceptance_criteria"))


@dataclass(frozen=True, slots=True)
class OrderEvent:
    from_status: OrderStatus | None
    to_status: OrderStatus
    actor_org_id: str
    reason: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class Order:
    order_id: str
    idempotency_key: str
    buyer_org_id: str
    seller_org_id: str
    listing_id: str
    listing_version: int
    capability_id: str
    capability_version: int
    listing_title: str
    price_snapshot: Money
    acceptance_criteria_snapshot: tuple[str, ...]
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    history: tuple[OrderEvent, ...]


_TRANSITIONS = {
    OrderStatus.PLACED: {OrderStatus.ACCEPTED, OrderStatus.REJECTED, OrderStatus.CANCELLED},
    OrderStatus.ACCEPTED: {OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED},
    OrderStatus.IN_PROGRESS: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
    OrderStatus.DELIVERED: {OrderStatus.ACCEPTED_BY_BUYER, OrderStatus.DISPUTED},
    OrderStatus.ACCEPTED_BY_BUYER: set(), OrderStatus.REJECTED: set(),
    OrderStatus.CANCELLED: set(), OrderStatus.DISPUTED: set(),
}
_SELLER_ACTIONS = {OrderStatus.ACCEPTED, OrderStatus.REJECTED, OrderStatus.IN_PROGRESS, OrderStatus.DELIVERED}
_BUYER_ACTIONS = {OrderStatus.ACCEPTED_BY_BUYER, OrderStatus.DISPUTED}


class MarketplaceEngine:
    """In-memory domain engine; inject a clock for reproducible tests."""

    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._capabilities: dict[str, Capability] = {}
        self._listings: dict[str, Listing] = {}
        self._orders: dict[str, Order] = {}
        self._idempotency: dict[str, tuple[str, str, str]] = {}

    def register_capability(self, capability: Capability) -> Capability:
        if not isinstance(capability, Capability):
            raise DomainError("capability must be a Capability")
        if capability.capability_id in self._capabilities:
            raise DomainError(f"duplicate capability: {capability.capability_id}")
        self._capabilities[capability.capability_id] = capability
        return capability

    def create_listing(self, *, listing_id: str, owner_org_id: str, capability_id: str,
                       version: int, title: str, description: str, price: Money,
                       acceptance_criteria: Iterable[str]) -> Listing:
        capability = self._capabilities.get(capability_id)
        if capability is None:
            raise NotFound(f"capability not found: {capability_id}")
        if capability.owner_org_id != owner_org_id:
            raise PermissionDenied("listing owner must match capability owner")
        if listing_id in self._listings:
            raise DomainError(f"duplicate listing: {listing_id}")
        listing = Listing(listing_id, owner_org_id, capability_id, capability.version, version,
                          title, description, price, tuple(acceptance_criteria))
        self._listings[listing_id] = listing
        return listing

    def get_listing(self, listing_id: str) -> Listing:
        try:
            return self._listings[listing_id]
        except KeyError as exc:
            raise NotFound(f"listing not found: {listing_id}") from exc

    def publish_listing(self, listing_id: str) -> Listing:
        current = self.get_listing(listing_id)
        if current.status is not ListingStatus.DRAFT:
            raise DomainError("only draft listings can be published")
        updated = replace(current, status=ListingStatus.PUBLISHED)
        self._listings[listing_id] = updated
        return updated

    def suspend_listing(self, listing_id: str) -> Listing:
        current = self.get_listing(listing_id)
        if current.status is not ListingStatus.PUBLISHED:
            raise DomainError("only published listings can be suspended")
        updated = replace(current, status=ListingStatus.SUSPENDED)
        self._listings[listing_id] = updated
        return updated

    def list_listings(self, *, status: ListingStatus | None = None) -> tuple[Listing, ...]:
        items = self._listings.values()
        if status is not None:
            items = (x for x in items if x.status is status)
        return tuple(sorted(items, key=lambda x: x.listing_id))

    def create_order(self, *, buyer_org_id: str, listing_id: str, idempotency_key: str) -> Order:
        _text(buyer_org_id, "buyer_org_id")
        _text(listing_id, "listing_id")
        _text(idempotency_key, "idempotency_key")
        prior = self._idempotency.get(idempotency_key)
        if prior:
            if prior[:2] != (buyer_org_id, listing_id):
                raise IdempotencyConflict("idempotency key already belongs to another request")
            return self._orders[prior[2]]
        listing = self.get_listing(listing_id)
        if listing.status is not ListingStatus.PUBLISHED:
            raise DomainError("only published listings can be ordered")
        if buyer_org_id == listing.owner_org_id:
            raise DomainError("self-purchase is not allowed")
        now = _now(self._clock)
        order_id = "ord_" + hashlib.sha256(idempotency_key.encode()).hexdigest()[:20]
        if order_id in self._orders:
            raise DomainError("order ID collision")
        initial = OrderEvent(None, OrderStatus.PLACED, buyer_org_id, "Order placed", now)
        order = Order(order_id, idempotency_key, buyer_org_id, listing.owner_org_id,
                      listing.listing_id, listing.version, listing.capability_id,
                      listing.capability_version, listing.title, listing.price,
                      listing.acceptance_criteria, OrderStatus.PLACED, now, now, (initial,))
        self._orders[order_id] = order
        self._idempotency[idempotency_key] = (buyer_org_id, listing_id, order_id)
        return order

    def get_order(self, order_id: str) -> Order:
        try:
            return self._orders[order_id]
        except KeyError as exc:
            raise NotFound(f"order not found: {order_id}") from exc

    def transition_order(self, *, order_id: str, actor_org_id: str,
                         target_status: OrderStatus, reason: str) -> Order:
        _text(actor_org_id, "actor_org_id")
        _text(reason, "reason")
        if not isinstance(target_status, OrderStatus):
            raise DomainError("target_status must be an OrderStatus")
        current = self.get_order(order_id)
        if target_status not in _TRANSITIONS[current.status]:
            raise InvalidTransition(f"{current.status.value} -> {target_status.value} is not allowed")
        if target_status in _SELLER_ACTIONS and actor_org_id != current.seller_org_id:
            raise PermissionDenied("seller organization required")
        if target_status in _BUYER_ACTIONS and actor_org_id != current.buyer_org_id:
            raise PermissionDenied("buyer organization required")
        if target_status is OrderStatus.CANCELLED and actor_org_id not in {current.buyer_org_id, current.seller_org_id}:
            raise PermissionDenied("only an order party can cancel")
        now = _now(self._clock)
        event = OrderEvent(current.status, target_status, actor_org_id, reason, now)
        updated = replace(current, status=target_status, updated_at=now, history=current.history + (event,))
        self._orders[order_id] = updated
        return updated

    def list_orders(self, *, status: OrderStatus | None = None) -> tuple[Order, ...]:
        items = self._orders.values()
        if status is not None:
            items = (x for x in items if x.status is status)
        return tuple(sorted(items, key=lambda x: x.order_id))
