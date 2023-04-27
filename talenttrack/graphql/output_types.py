import graphene
from graphene_django import DjangoObjectType

from ..models import (
    Achievements,
    Awards,
    Publications,
    Result,
    CourseType,
    LicenseCertification,
    Course,
    Topic,
    Lecturer,
    ClassMates,
    Designation,
    WorkExperience,
    WorkColleague,
    Superior,
    WorkCollaborator,
    WorkClient,
    EmailRemindValidate
)

from locations.graphql.output_types import CountryFieldType


class AchievementOutputType(DjangoObjectType):
    class Meta:
        model = Achievements
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'talent__alias': ['exact'],
            'date_achieved': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'upload': ['exact'],
            'slug': ['exact'],
        }
        
        
class AwardsOutputType(DjangoObjectType):
    class Meta:
        model = Awards
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'talent__alias': ['exact'],
            'award': ['exact', 'icontains', 'startswith'],
            'date_achieved': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'tag': ['exact', 'icontains', 'startswith'],
            'upload': ['exact'],
            'slug': ['exact'],
        }
        
        
class PublicationsOutputType(DjangoObjectType):
    class Meta:
        model = Publications
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enums = ['type']
        filter_fields = {
            'talent__alias': ['exact'],
            'title': ['exact', 'icontains', 'startswith'],
            'type': ['exact'],
            'publisher__publisher': ['exact', 'icontains', 'startswith'],
            'link': ['exact', 'icontains', 'startswith'],
            'author__name': ['exact', 'icontains', 'startswith'],
            'tag__skill': ['exact', 'icontains', 'startswith'],
            'tag__code': ['exact', 'icontains', 'startswith'],
            'genre__name': ['exact', 'icontains', 'startswith'],
            'date_published': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'upload': ['exact'],
            'slug': ['exact'],
        }
        
        
class ResultOutputType(DjangoObjectType):
    class Meta:
        model = Result
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'type': ['exact', 'icontains', 'startswith'],
        }
        
        
class CourseTypeOutputType(DjangoObjectType):
    class Meta:
        model = CourseType
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'type': ['exact', 'icontains', 'startswith'],
        }
        
        
class LicenseCertificationOutputType(DjangoObjectType):
    country = CountryFieldType()
    
    class Meta:
        model = LicenseCertification
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'talent__alias': ['exact'],
            'certification__type': ['exact', 'icontains', 'startswith'],
            'cert_name': ['exact', 'icontains', 'startswith'],
            'country': ['exact'],
            'region__region': ['exact', 'icontains', 'startswith'],
            'cm_no': ['exact', 'icontains', 'startswith'],
            'companybranch__ename': ['exact', 'icontains', 'startswith'],
            'upload': ['exact'],
            'issue_date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'expiry_date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'current': ['exact'],
            'slug': ['exact'],
        }
        
        
class CourseOutputType(DjangoObjectType):
    class Meta:
        model = Course
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'name': ['exact', 'icontains', 'startswith'],
            'company__ename':['exact', 'icontains', 'startswith'],
            'course_type__type': ['exact', 'icontains', 'startswith'],
            'website': ['exact', 'icontains', 'startswith'],
            'certification__type': ['exact', 'icontains', 'startswith'],
        }
        
        
class TopicOutputType(DjangoObjectType):
    class Meta:
        model = Topic
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'topic': ['exact', 'icontains', 'startswith'],
            'skills__skill': ['exact', 'icontains', 'startswith'],
            'hours': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
        
        
class LecturerOutputType(DjangoObjectType):
    class Meta:
        model = Lecturer
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = ['confirm']
        filter_fields = {
            'education__talent__alias': ['exact'],
            'lecturer__alias': ['exact'],
            'topic__topic': ['exact', 'icontains', 'startswith'],
            'date_captured': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date_confirmed': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'locked': ['exact'],
            'confirm': ['exact'],
            'publish_comment': ['exact'],
            'slug': ['exact'],
        }
        
        
class ClassMatesOutputType(DjangoObjectType):
    class Meta:
        model = ClassMates
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = ['confirm']
        filter_fields = {
            'education__talent__alias': ['exact'],
            'colleague__alias': ['exact'],
            'topic__topic': ['exact', 'icontains', 'startswith'],
            'date_captured': [''],
            'date_confirmed': [''],
            'locked': ['exact'],
            'confirm': ['exact'],
            'publish_comment': ['exact'],
            'slug': ['exact'],
        }
        
        
class DesignationOutputType(DjangoObjectType):
    class Meta:
        model = Designation
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'name': ['exact', 'icontains', 'startswith'],
        }
        
        
class WorkExperienceOutputType(DjangoObjectType):
    class Meta:
        model = WorkExperience
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = ['employment_type']
        filter_fields = {
            'talent__alias': ['exact'],
            'date_from': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date_to': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date_captured': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'upload': ['exact'],
            'score': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'employment_type': ['exact'],
            'title': ['exact', 'icontains', 'startswith'],
            'publish_comment': ['exact'],
            'not_validated': ['exact'],
            'company__ename': ['exact', 'icontains', 'startswith'],
            'companybranch__name': ['exact', 'icontains', 'startswith'],
            'estimated': ['exact'],
            'prelog': ['exact'],
            'wexp': ['exact'],
            'project__name': ['exact', 'icontains', 'startswith'],
            'project_data__talent__alias': ['exact'],
            'industry__industry': ['exact', 'icontains', 'startswith'],
            'hours_worked': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'designation__name': ['exact', 'icontains', 'startswith'],
            'skills__skill': ['exact', 'icontains', 'startswith'],
            'edt': ['exact'],
            'course__name': ['exact', 'icontains', 'startswith'],
            'topic__topic': ['exact', 'icontains', 'startswith'],
            'slug': ['exact'],
        }
        
        
class WorkColleagueOutputType(DjangoObjectType):
    class Meta:
        model = WorkColleague
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = ['confirm']
        filter_fields = {
            'experience__talent__alias': ['exact'],
            'colleague_name__alias': ['exact'],
            'designation__name': ['exact', 'icontains', 'startswith'],
            'date_captured': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date_confirmed': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'locked': ['exact'],
            'confirm': ['exact'],
            'publish_comment': ['exact'],
            'quality': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'time_taken': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'complexity': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'slug': ['exact'],
        }
        
        
class SuperiorOutputType(DjangoObjectType):
    class Meta:
        model = Superior
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = ['confirm']
        filter_fields = {
            'experience__talent__alias': ['exact'],
            'superior_name__alias': ['exact'],
            'designation__name': ['exact', 'icontains', 'startswith'],
            'date_captured': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date_confirmed': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'locked': ['exact'],
            'confirm': ['exact'],
            'publish_comment': ['exact'],
            'quality': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'time_taken': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'complexity': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'slug': ['exact'],
        }
        
        
class WorkCollaboratorOutputType(DjangoObjectType):
    class Meta:
        model = WorkCollaborator
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = ['confirm']
        filter_fields = {
            'experience__talent__alias': ['exact'],
            'collaborator_name__alias': ['exact'],
            'designation__name': ['exact', 'icontains', 'startswith'],
            'date_captured': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date_confirmed': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'locked': ['exact'],
            'confirm': ['exact'],
            'publish_comment': ['exact'],
            'quality': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'time_taken': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'complexity': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'slug': ['exact'],
        }
        
        
class WorkClientOutputType(DjangoObjectType):
    class Meta:
        model = WorkClient
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        convert_choices_to_enum = ['confirm']
        filter_fields = {
            'experience__talent__alias': ['exact'],
            'client_name__alias': ['exact'],
            'designation__name': ['exact', 'icontains', 'startswith'],
            'date_captured': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date_confirmed': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'locked': ['exact'],
            'confirm': ['exact'],
            'publish_comment': ['exact'],
            'quality': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'time_taken': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'complexity': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'slug': ['exact'],
        }
        
        
class EmailRemindValidateOutputType(DjangoObjectType):
    class Meta:
        model = EmailRemindValidate
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'sender__alias': ['exact'],
            'recipient__alias': ['exact'],
            'date_sent': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }