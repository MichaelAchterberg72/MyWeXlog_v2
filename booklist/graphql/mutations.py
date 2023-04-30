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


class PublisherUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = PublisherInputType.id
        publisher = PublisherInputType.publisher
        link = PublisherInputType.link
        
    Output = graphene.Field(
        lambda: graphene.Union("PublisherUpdateOrCreateResult", 
                               [SuccessMessage, FailureMessage]))
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                publisher_id = kwargs.pop('id', None)
                if publisher_id:
                    kwargs['id'] = publisher_id
                    
                publisher, created = Publisher.objects.update_or_create(**kwargs)
                message = "Publisher updated successfully" if not created else "Publisher created successfully"
                return SuccessMessage(success=True, id=publisher.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding publisher: {str(e)}")


class PublisherDelete(graphene.Mutation):
    class Arguments:
        id = PublisherInputType.id
        
    Output = graphene.Field(
        lambda: graphene.Union("PublisherDeleteResult", 
                               [SuccessMessage, FailureMessage]))
        
    def mutate(self, root, info, **kwargs):
        try:
            with transaction.atomic():
                publisher = Publisher.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'] message="Publisher deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting publisher: {str(e)}")


class GenreUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = GenreInputType.id
        name = GenreInputType.name
        
    Output = graphene.Field(
        lambda: graphene.Union("GenreUpdateOrCreateResult", 
                               [SuccessMessage, FailureMessage]))
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                genre_id = kwargs.pop('id', None)
                if genre_id:
                    kwargs['id'] = genre_id
                    
                genre, created = Genre.objects.update_or_create(**kwargs)
                message = "Genre updated successfully" if not created else "Genre created successfully"
                return SuccessMessage(success=True, id=genre.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding genre: {str(e)}")


class GenreDelete(graphene.Mutation):
    class Arguments:
        id = GenreInputType.id
        
    Output = graphene.Field(
        lambda: graphene.Union("GenreDeleteResult", 
                               [SuccessMessage, FailureMessage]))
        
    def mutate(self, root, info, **kwargs):
        try:
            with transaction.atomic():
                genre = Genre.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'] message="Genre deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting genre: {str(e)}")


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