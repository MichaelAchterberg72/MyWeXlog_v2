import phonenumbers
from django import template
import nltk
#TODO
#nltk.download('punkt')
import truecase
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("merge_entities")

register = template.Library()


@register.filter
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)


@register.filter(name='phonenumber')
def phonenumber(value, country=None):
   return phonenumbers.parse(value, country)


@register.filter(name='replacenames')
def replacenames(text):
    text = truecase.get_true_case(text)
    text_doc = nlp(text)
    result = []
    for t in text_doc:
        if t.ent_type_ == "PERSON":
            result.append("[NAME]")
        else:
            result.append(t.text)
        result.append(t.whitespace_)

    res = str(''.join(result))
    return res
