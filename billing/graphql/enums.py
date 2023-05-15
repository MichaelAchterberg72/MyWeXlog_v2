import graphene
from utils.utils import create_enum_from_choices


class TimesheetRepeatEnum(graphene.Enum):
    H = 'Doesn\'t repeat'
    D = 'Daily'
    W = 'Weekly'
    M = 'Monthly'
    A = 'Annualy'
    L = 'Every weekday (Monday to Friday)'
    C = 'Custom'
    
    
class TimesheetBusyEnum(graphene.Enum):
    B = 'Busy'
    F = 'Free'
    
    
class TimesheetNotificationEnum(graphene.Enum):
    E = 'Email'
    N = 'Notification'
    
    
class TimesheetDurationEnum(graphene.Enum):
    M = 'minutes'
    H = 'hours'
    D = 'days'
    W = 'weeks'