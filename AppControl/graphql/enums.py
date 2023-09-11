import graphene
from django.db import models


class SubChoices(models.IntegerChoices):
    LIGHT = 0
    MEDIUM = 1
    HEAVY = 2


SubEnum = graphene.Enum.from_enum(SubChoices)