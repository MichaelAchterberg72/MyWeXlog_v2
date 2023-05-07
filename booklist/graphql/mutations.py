import graphene
from django.db import transaction

from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult

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
        
    Output = SuccessMutationResult
        
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
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                author = Author.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Author deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting author: {str(e)}")


class PublisherUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = PublisherInputType.id
        publisher = PublisherInputType.publisher
        link = PublisherInputType.link
        
    Output = SuccessMutationResult
        
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
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                publisher = Publisher.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Publisher deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting publisher: {str(e)}")


class GenreUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = GenreInputType.id
        name = GenreInputType.name
        
    Output = SuccessMutationResult
        
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
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                genre = Genre.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Genre deleted successfully")
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
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                booklist_id = kwargs.pop('id', None)
                booklist = BookList.update_or_create(id=booklist_id, **kwargs)
                message = "BookList updated successfully" if booklist_id else "BookList created successfully"
                return SuccessMessage(success=True, id=booklist.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding booklist: {str(e)}")


class BookListDelete(graphene.Mutation):
    class Arguments:
        slug = BookListInputType.slug
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                booklist = BookList.objects.get(kwargs['slug']).delete()
                return SuccessMessage(success=True, id=kwargs['slug'], message="BookList deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting booklist: {str(e)}")


class FormatUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = FormatInputType.id
        format = FormatInputType.format
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                format_id = kwargs.pop('id', None)
                if format_id:
                    kwargs['id'] = format_id
                    
                format, created = Format.objects.update_or_create(**kwargs)
                message = "Format updated successfully" if not created else "Format created successfully"
                return SuccessMessage(success=True, id=format.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding format: {str(e)}")


class FormatDelete(graphene.Mutation):
    class Arguments:
        id = FormatInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                format = Format.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Format deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting format: {str(e)}")


class ReadByUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = ReadByInputType.id
        talent = ReadByInputType.talent
        book = ReadByInputType.book
        type = ReadByInputType.type
        date = ReadByInputType.date
        review = ReadByInputType.review
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                readby_id = kwargs.pop('id', None)
                if readby_id:
                    kwargs['id'] = readby_id
                    
                readby, created = ReadBy.objects.update_or_create(**kwargs)
                message = "ReadBy updated successfully" if not created else "ReadBy created successfully"
                return SuccessMessage(success=True, id=readby.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding readby: {str(e)}")


class ReadByDelete(graphene.Mutation):
    class Arguments:
        id = ReadByInputType.id
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            with transaction.atomic():
                booklist = ReadBy.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="ReadBy deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting readby: {str(e)}")

        
class Mutation(graphene.ObjectType):
    author_update_or_create = AuthorUpdateOrCreate.Field()
    author_delete = AuthorDelete.Field()
    publisher_update_or_create = PublisherUpdateOrCreate.Field()
    publisher_delete = PublisherDelete.Field()
    genre_update_or_create = GenreUpdateOrCreate.Field()
    genre_delete = GenreDelete.Field()
    booklist_update_or_create = BookListUpdateOrCreate.Field()
    booklist_delete = BookListDelete.Field()
    format_update_or_create = FormatUpdateOrCreate.Field()
    format_delete = FormatDelete.Field()