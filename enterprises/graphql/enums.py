from ..models import Enterprise, Branch
from utils.utils import create_enum_from_choices


EnterpriseFCEnum = create_enum_from_choices(Enterprise.FC)
BranchSizeEnum = create_enum_from_choices(Branch.SZE)