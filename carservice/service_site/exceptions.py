class BusinessLogicError(Exception):
    """Base exception for business logic errors."""
    pass

class ProcurementIsCompletedError(BusinessLogicError):
    pass

class NotEnoughPartsError(BusinessLogicError):
    pass

class InvalidPlacementError(BusinessLogicError):
    pass

class UnitHasPlacementsError(BusinessLogicError):
    pass

class InvalidProcurementUnitData(BusinessLogicError):
    pass

class InvalidVisitServiceData(BusinessLogicError):
    pass