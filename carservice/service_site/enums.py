from enum import Enum

class VisitStatusEnum(str, Enum):
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"

class ProcurementStatusEnum(str, Enum):
    REJECTED = "Rejected"
    IN_PROGRESS = "In progress"
    DELIVERED = "Delivered"
    APPROVED = "Approved"

class PaymentStatusEnum(str, Enum):
    REFUNDED = "Refunded"
    PENDING = "Pending"
    PAID = "Paid"
    CANCELLED = "Cancelled"