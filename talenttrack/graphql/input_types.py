import graphene
from graphene_file_upload.scalars import Upload

from users.graphql.input_types import UserInputType
from db_flatten.graphql.input_types import SkillTagInputType
from booklist.graphql.input_types import (
    AuthorInputType, 
    PublisherInputType, 
    GenreInputType,
    BookListInputType,
    ReadByInputType
)
from locations.graphql.input_types import CountryFieldInputType, RegionInputType
from enterprises.graphql.input_types import EnterpriseInputType, BranchInputType, IndustryInputType
from project.graphql.input_types import ProjectDataInputType, ProjectPersonalDetailsInputType


class AchievementsInputType(graphene.InputObjectType):
    talent = graphene.Field(UserInputType)
    achievement = graphene.String()
    date_achieved = graphene.Date()
    description = graphene.String()
    upload = Upload()
    slug = graphene.String()
    
    
class AwardsInputType(graphene.InputObjectType):
    talent = graphene.Field(UserInputType)
    award = graphene.String()
    date_achieved = graphene.Date()
    description = graphene.String()
    tag = graphene.List(SkillTagInputType)
    upload = Upload()
    thumbnail = Upload()
    slug = graphene.String()
    
    
class PublicationsInputType(graphene.InputObjectType):
    talent = graphene.Field(UserInputType)
    title = graphene.String()
    type = graphene.String()
    publisher = graphene.Field(PublisherInputType)
    link = graphene.String()
    author = graphene.List(AuthorInputType)
    tag = graphene.List(SkillTagInputType)
    genre = graphene.List(GenreInputType)
    date_published = graphene.Date()
    description = graphene.String()
    upload = Upload()
    slug = graphene.String()
    
    
class ResultInputType(graphene.InputObjectType):
    type = graphene.String()
    
    
class CourseTypeInputType(graphene.InputObjectType):
    type = graphene.String()
    
    
class LicenseCertificationInputType(graphene.InputObjectType):
    talent = graphene.Field(UserInputType)
    certification = graphene.Argument(ResultInputType)
    cert_name = graphene.String()
    country = CountryFieldInputType(required=True)
    region = graphene.Field(RegionInputType)
    cm_no = graphene.String()
    companybranch = graphene.Field(EnterpriseInputType)
    upload = Upload()
    issue_date = graphene.Date()
    expiry_date = graphene.Date()
    current = graphene.Boolean()
    slug = graphene.String()
    
    
class CourseInputType(graphene.InputObjectType):
    name = graphene.String()
    company = graphene.Field(EnterpriseInputType)
    course_type = graphene.Field(CourseTypeInputType)
    website = graphene.String()
    certification = graphene.Field(ResultInputType)
    
    
class TopicInputType(graphene.InputObjectType):
    topic = graphene.String()
    skills = graphene.List(SkillTagInputType)
    hours = graphene.Decimal()
    
    
class LecturerInputType(graphene.InputObjectType):
    education = graphene.Field(lambda: WorkExperienceInputType)
    lecturer = graphene.Field(UserInputType)
    topic = graphene.Field(TopicInputType)
    date_captured = graphene.Date()
    date_confirmed = graphene.Date()
    locked = graphene.Boolean()
    confirm = graphene.String()
    comments = graphene.String()
    publish_comment = graphene.Boolean()
    response = graphene.String()
    slug = graphene.String()
    
    
class ClassMatesInputType(graphene.InputObjectType):
    education = graphene.Field(lambda: WorkExperienceInputType)
    colleague = graphene.Field(UserInputType)
    topic = graphene.Field(TopicInputType)
    date_captured = graphene.Date()
    date_confirmed = graphene.Date()
    locked = graphene.Boolean()
    confirm = graphene.String()
    comments = graphene.String()
    publish_comment = graphene.Boolean()
    response = graphene.String()
    slug = graphene.String()
    
    
class DesignationInputType(graphene.InputObjectType):
    name = graphene.String()
    
    
class WorkExperienceInputType(graphene.InputObjectType):
    talent = graphene.Field(UserInputType)
    date_from = graphene.Date()
    date_to = graphene.Date()
    date_captured = graphene.Date()
    upload = Upload()
    score = graphene.Int()
    employment_type = graphene.String()
    title = graphene.String()
    comment = graphene.String()
    publish_comment = graphene.Boolean()
    not_validated = graphene.Boolean()
    company = graphene.Field(EnterpriseInputType)
    companybranch = graphene.Field(BranchInputType)
    estimated = graphene.Boolean()
    prelog = graphene.Boolean()
    wexp = graphene.Boolean()
    project = graphene.Field(ProjectDataInputType)
    project_data = graphene.Field(ProjectPersonalDetailsInputType)
    industry = graphene.Field(IndustryInputType)
    hours_worked = graphene.Decimal()
    designation = graphene.Field(DesignationInputType)
    skills = graphene.List(SkillTagInputType)
    edt = graphene.Boolean()
    course = graphene.Field(CourseInputType)
    topic = graphene.Field(TopicInputType)
    slug = graphene.String()
    
    
class WorkColleagueInputType(graphene.InputObjectType):
    experience = graphene.Field(lambda: WorkExperienceInputType)
    colleague_name = graphene.Field(UserInputType)
    designation = graphene.Field(DesignationInputType)
    date_captured = graphene.Date()
    date_confirmed = graphene.Date()
    locked = graphene.Boolean()
    confirm = graphene.String()
    comments = graphene.String()
    publish_comment = graphene.Boolean()
    quality = graphene.Decimal()
    time_taken = graphene.Decimal()
    complexity = graphene.Decimal()
    response = graphene.String()
    slug = graphene.String()
    
    
class SuperiorInputType(graphene.InputObjectType):
    experience = graphene.Field(lambda: WorkExperienceInputType)
    superior_name = graphene.Field(UserInputType)
    designation = graphene.Field(DesignationInputType)
    date_captured = graphene.Date()
    date_confirmed = graphene.Date()
    locked = graphene.Boolean()
    confirm = graphene.String()
    comments = graphene.String()
    publish_comment = graphene.Boolean()
    quality = graphene.Decimal()
    time_taken = graphene.Decimal()
    complexity = graphene.Decimal()
    response = graphene.String()
    slug = graphene.String()
    
    
class WorkCollaboratorInputType(graphene.InputObjectType):
    experience = graphene.Field(lambda: WorkExperienceInputType)
    collaborator_name = graphene.Field(UserInputType)
    designation = graphene.Field(DesignationInputType)
    date_captured = graphene.Date()
    date_confirmed = graphene.Date()
    locked = graphene.Boolean()
    confirm = graphene.String()
    comments = graphene.String()
    publish_comment = graphene.Boolean()
    quality = graphene.Decimal()
    time_taken = graphene.Decimal()
    complexity = graphene.Decimal()
    response = graphene.String()
    slug = graphene.String()
    
    
class WorkClientInputType(graphene.InputObjectType):
    experience = graphene.Field(lambda: WorkExperienceInputType)
    client_name = graphene.Field(UserInputType)
    designation = graphene.Field(DesignationInputType)
    date_captured = graphene.Date()
    date_confirmed = graphene.Date()
    locked = graphene.Boolean()
    confirm = graphene.String()
    comments = graphene.String()
    publish_comment = graphene.Boolean()
    quality = graphene.Decimal()
    time_taken = graphene.Decimal()
    complexity = graphene.Decimal()
    response = graphene.String()
    slug = graphene.String()
    
    
class EmailRemindValidateInputType(graphene.InputObjectType):
    sender = graphene.Field(UserInputType)
    recipient = graphene.Field(UserInputType)
    subject = graphene.String()
    message = graphene.String()
    date_sent = graphene.DateTime()