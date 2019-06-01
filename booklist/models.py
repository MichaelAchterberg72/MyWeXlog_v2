from django.db import models
from django.conf import settings

from db_flatten.models import SkillTag

class Author(models.Model):
    name = models.CharField('Author name', max_length=250, unique=True)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    publisher = models.CharField(max_length=150, unique=True)
    def __str__(self):
        return self.publisher

class BookList(models.Model):
    title = models.CharField('Book Title', max_length=300, unique=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    link = models.URLField('Book URL', blank=True, null=True)
    author = models.ManyToManyField(Author)
    tag = models.ManyToManyField(SkillTag)

    class Meta:
        unique_together = (('title', 'publisher'),)

    def __str__(self):
        return '{}, {}'.format(self.title, self.publisher)

class Format(models.Model):
    format = models.CharField(max_length=60, unique=True)

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
