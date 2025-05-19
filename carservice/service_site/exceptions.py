class BusinessLogicError(Exception):
    """Base exception for business logic errors."""
    pass

class ProcurementIsCompletedError(BusinessLogicError):
    pass

class NotEnoughPartsError(BusinessLogicError):
    pass