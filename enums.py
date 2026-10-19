from enum import Enum


class AdStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESERVED = "RESERVED"
    CLOSED = "CLOSED"


class OrderStatus(str, Enum):
    PAID_HOLD = "PAID_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
