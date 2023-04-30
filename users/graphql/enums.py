from ..models import CustomUser
from utils.utils import create_enum_from_choices


UserPKGEnum = create_enum_from_choices(CustomUser.PKG)
UserCompanyEnum = create_enum_from_choices(CustomUser.COMPANY)
UserRoleEnum = create_enum_from_choices(CustomUser.ROLE)
UserPaidTypeEnum = create_enum_from_choices(CustomUser.PAID_TYPE)