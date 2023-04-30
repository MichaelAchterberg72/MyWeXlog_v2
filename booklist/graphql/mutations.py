import graphene
from django.db import transaction

from utils.graphql.output_types import SuccessMessage, FailureMessage

from .input_types import (
    AuthorInputType,
    PublisherInputType,
    GenreInputType,
    BookListInputType,
    FormatInputType,
    ReadByInputType
)

from ..models import (
    Author,
    Publisher,
    Genre,
    BookList,
    Format,
    ReadBy
)


class AuthorUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = AuthorInputType.id
        name = AuthorInputType.name
        
    Output = graphene.Field(
        lambda: graphene.Union("AuthorUpdateOrCreateResult", 
                               [SuccessMessage, FailureMessage]))
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                author_id = kwargs.pop('id', None)
                if author_id:
                    kwargs['id'] = author_id
                    
                author, created = Author.objects.update_or_create(**kwargs)
                message = "Author updated successfully" if not created else "Author created successfully"
                return SuccessMessage(success=True, id=author.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding author: {str(e)}")


class AuthorDelete(graphene.Mutation):
    class Arguments:
        id = AuthorInputType.id
        
    Output = graphene.Field(
        lambda: graphene.Union("AuthorDeleteResult", 
                               [SuccessMessage, FailureMessage]))
        
    def mutate(self, root, info, **kwargs):
        try:
            with transaction.atomic():
                author = Author.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'] message="Author deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting author: {str(e)}")


class BookListUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = BookListInputType.id
        title = BookListInputType.title
        type = BookListInputType.type
        publisher = BookListInputType.publisher
        link = BookListInputType.link
        author = BookListInputType.author
        tag = BookListInputType.tag
        genre = BookListInputType.genre
        slug = BookListInputType.slug
        
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                booklist_id = kwargs.pop('id', None)
                booklist = BookList.update_or_create(id=booklist_id, **kwargs)
                message = "BookList updated successfully" if booklist_id else "BookList created successfully"
                return SuccessMessage(success=True, id=booklist.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding booklist: {str(e)}")


        
graphene.Schema.register_union_type("AuthorDeleteResult", [SuccessMessage, FailureMessage])

class Mutation(graphene.ObjectType):
    delete_author = AuthorDelete.Field()