from django.conf import settings
from django.db import models

from tinymce.models import HTMLField

from utils.utils import update_model, handle_m2m_relationship

from users.models import CustomUser
from db_flatten.models import SkillTag
from Profile.utils import create_code9


class Author(models.Model):
    name = models.CharField('Author name', max_length=250, unique=True)

    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = Author.objects.get(pk=id)

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = Author.objects.create(**kwargs)
        return instance

    def clean(self):
        self.name = self.name.title()
        
    def __str__(self):
        return self.name


class Publisher(models.Model):
    publisher = models.CharField(max_length=150, unique=True)
    link = models.URLField('Publisher URL', blank=True, null=True)

    def clean(self):
        self.publisher = self.publisher.title()
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = Publisher.objects.get(pk=id)

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = Publisher.objects.create(**kwargs)
        return instance

    def __str__(self):
        return self.publisher


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def clean(self):
        self.name = self.name.title()
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = Genre.objects.get(pk=id)

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = Genre.objects.create(**kwargs)
        return instance

    def __str__(self):
        return f'{self.name}'


class BookList(models.Model):
    CLASS=(
        ('F','Fiction'),
        ('N','Non-fiction'),
    )
    title = models.CharField('Book Title', max_length=300, unique=True)
    type = models.CharField(max_length=1, choices=CLASS, default='F' )
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    link = models.URLField('Book URL', blank=True, null=True)
    author = models.ManyToManyField(Author)
    tag = models.ManyToManyField(SkillTag, verbose_name='Tag / Associated Skill')
    genre = models.ManyToManyField(Genre)
    slug = models.SlugField(max_length=60, unique=True, blank=True, null=True)

    class Meta:
        unique_together = (('title', 'publisher'),)
    
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = BookList.objects.get(pk=id)
            
        publisher = kwargs.pop('publisher', None)
        author = kwargs.pop('author', [])
        tag = kwargs.pop('tag', [])
        genre = kwargs.pop('genre', [])

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = BookList.objects.create(**kwargs)
            
        if publisher:
            instance = Publisher.update_or_create(instance=instance, **publisher)

        if author:
            author_related_models_data = {
                'author': (Author, cls.author, ['name']),
            }
            instance = handle_m2m_relationship(instance, author_related_models_data)

        if tag:
            tag_related_models_data = {
                'tag': (SkillTag, cls.tag, ['skill', 'code']),
            }
            instance = handle_m2m_relationship(instance, tag_related_models_data)

        if genre:
            genre_related_models_data = {
                'genre': (Genre, cls.genre, ['name']),
            }
            instance = handle_m2m_relationship(instance, genre_related_models_data)

        return instance

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(BookList, self).save(*args, **kwargs)


#The format of the book (softback, hardcover, E-book, Abridged/Summary, audiobook,  etc.)
class Format(models.Model):
    format = models.CharField(max_length=60, unique=True)

    def clean(self):
        self.format = self.format.title()
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = Format.objects.get(pk=id)

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = Format.objects.create(**kwargs)
        return instance

    def __str__(self):
        return self.format


class ReadBy(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(BookList, on_delete=models.PROTECT)
    type = models.ForeignKey(Format, on_delete=models.PROTECT, verbose_name='Book Format')
    date = models.DateField('Date Finished')
    review = HTMLField(blank=True, null=True)

    class Meta:
        unique_together = (('talent','book'),)
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = ReadBy.objects.get(pk=id)
            
        talent = kwargs.pop('talent', None)
        book = kwargs.pop('book', None)
        type = kwargs.pop('type', None)

        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = ReadBy.objects.create(**kwargs)
            
        if talent:
            instance = CustomUser.update_or_create(instance=instance, **talent)

        if book:
            instance = BookList.update_or_create(instance=instance, **book)

        if type:
            instance = Format.update_or_create(instance=instance, **type)

        return instance

    def __str__(self):
        return '{} read {}'.format(self.talent, self.book)
