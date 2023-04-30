from ..models import REPEAT, BUSY, NOTIFICATION, DURATION
from utils.utils import create_enum_from_choices


TimesheetRepeatEnum = create_enum_from_choices(REPEAT)
TimesheetBusyEnum = create_enum_from_choices(BUSY)
TimesheetNotificationEnum = create_enum_from_choices(NOTIFICATION)
TimesheetDurationEnum = create_enum_from_choices(DURATION)