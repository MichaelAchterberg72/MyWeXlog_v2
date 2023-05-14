import graphene
from ..models import BookList
# from utils.utils import create_enum_from_choices


# BookClassEnum = create_enum_from_choices(BookList.CLASS)

class BookClassEnum(graphene.Enum):
    F = 'Fiction'
    N = 'Non_fiction'