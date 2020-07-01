from django.db import models
from django.conf import settings

from db_flatten.models import SkillTag

from Profile.utils import create_code9

class Author(models.Model):
    name = models.CharField('Author name', max_length=250, unique=True)

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.title()


class Publisher(models.Model):
    publisher = models.CharField(max_length=150, unique=True)
    link = models.URLField('Publisher URL', blank=True, null=True)

    def clean(self):
        self.publisher = self.publisher.title()

    def __str__(self):
        return self.publisher


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def clean(self):
        self.name = self.name.title()

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

    def __str__(self):
        return '{}, {}'.format(self.title, self.publisher)

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_code9(self)

        super(BookList, self).save(*args, **kwargs)


#The format of the book (softback, hardcover, E-book, Abridged/Summary, audiobook,  etc.)
class Format(models.Model):
    format = models.CharField(max_length=60, unique=True)

    def clean(self):
        self.format = self.format.title()

    def __str__(self):
        return self.format


class ReadBy(models.Model):
    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(BookList, on_delete=models.PROTECT)
    type = models.ForeignKey(Format, on_delete=models.PROTECT, verbose_name='Book_format')
    date = models.DateField('Date Finished')

    class Meta:
        unique_together = (('talent','book'),)

    def __str__(self):
        return '{} read {}'.format(self.talent, self.book)
