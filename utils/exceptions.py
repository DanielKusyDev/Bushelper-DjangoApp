class WeekdaysValueError(ValueError):
    """Raised when weekdays not in (0,6)"""
    pass


class NoCoursesAvailableError(ValueError):
    """Raised when there is no available courses"""
    pass


class SameBusStopError(Exception):
    pass