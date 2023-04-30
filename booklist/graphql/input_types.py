import graphene

from db_flatten.graphql.input_types import SkillTagInputType
from users.graphql.input_types import UserInputType


class AuthorInputType(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    
    
class PublisherInputType(graphene.InputObjectType):
    id = graphene.ID()
    publisher = graphene.String()
    link = graphene.String()
    
    
class GenreInputType(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    
    
class BookListInputType(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    type = graphene.String()
    publisher = graphene.Argument(PublisherInputType)
    link = graphene.String()
    author = graphene.List(AuthorInputType)
    tag = graphene.String(SkillTagInputType)
    genre = graphene.List(GenreInputType)
    slug = graphene.String()
    
    
class FormatInputType(graphene.InputObjectType):
    id = graphene.ID()
    format = graphene.String()
    
    
class ReadByInputType(graphene.InputObjectType):
    id = graphene.ID()
    talent = graphene.Argument(UserInputType)
    book = graphene.Argument(BookListInputType)
    type = graphene.Field(FormatInputType)
    date = graphene.Date()
    review = graphene.String()