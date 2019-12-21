from django import forms
from django.contrib.auth.models import User


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


from django_select2.forms import (
    ModelSelect2TagWidget, ModelSelect2Widget, Select2MultipleWidget,
    Select2Widget, ModelSelect2MultipleWidget
)


from .models import BookList, Author, ReadBy, Format, Publisher
from db_flatten.models import SkillTag

#>>> Select 2 Widgets
class PublisherSearchFieldMixin:
    search_fields = [
        'publisher__icontains', 'pk__startswith'
    ]

class PublisherSelect2Widget(PublisherSearchFieldMixin, ModelSelect2Widget):
    model = Publisher

    def create_value(self, value):
        self.get_queryset().create(publisher=value)


class TagSearchFieldMixin:
    search_fields = [
        'skill__icontains', 'pk__startswith'
    ]

class TagModelSelect2MultipleWidget(TagSearchFieldMixin, ModelSelect2MultipleWidget):
    model = SkillTag

    def create_value(self, value):
        self.get_queryset().create(skill=value)


class AuthorSearchFieldMixin:
    search_fields = [
        'name__icontains', 'pk__startswith'
    ]

class AuthorModelSelect2MultipleWidget(AuthorSearchFieldMixin, ModelSelect2MultipleWidget):
    model = Author

    def create_value(self, value):
        self.get_queryset().create(name=value)
#Select 2 Widget <<<


class BookAddForm(forms.ModelForm):
    class Meta:
        model = BookList
        fields = ('title','publisher','author','tag','link', 'type')
        widgets = {
            'publisher': PublisherSelect2Widget(),
            'tag': TagModelSelect2MultipleWidget(),
            'author': AuthorModelSelect2MultipleWidget(),
        }
        lables ={
            'tag':'Tag / Associated Skill'
        }


class AuthorAddForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["name",]


class PublisherAddForm(forms.ModelForm):
    class Meta:
        model=Publisher
        fields=("publisher", 'link')


class FormatAddForm(forms.ModelForm):
    class Meta:
        model=Format
        fields=('format',)


class TagAddForm(forms.ModelForm):
    class Meta:
        model = SkillTag
        fields = ["skill",]


class BookSearchFieldMixin:
    search_fields = [
        'title__icontains', 'pk__startswith'
    ]


class BookSelect2Widget(BookSearchFieldMixin, ModelSelect2Widget):
    model = BookList

    def create_value(self, value):
        self.get_queryset().create(title=value)


class TypeSearchFieldMixin:
    search_fields = [
        'format__icontains', 'pk__startswith'

    ]
class TypeSelect2Widget(TypeSearchFieldMixin, ModelSelect2Widget):
    model = Format

    def create_value(self, value):
        self.get_queryset().create(format=value)


class DateInput(forms.DateInput):
    input_type = 'date'


class AddBookReadForm(forms.ModelForm):
    class Meta:
        model = ReadBy
        fields = ('book','type','date',)
        widgets = {
            'date': DateInput(),
            'book': BookSelect2Widget(),
            'type': TypeSelect2Widget(),
        }


class DateForm(forms.Form):
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )


class BookSearchForm(forms.Form):
    query = forms.CharField()
