import graphene
from graphene_file_upload.scalars import Upload

from users.graphql.input_types import UserInputType
from skills.graphql.input_types import SkillTagInputType
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


class AchievementsInputType(graphene.InputType):
    talent = graphene.Field(UserInputType)
    achievement = graphene.String()
    date_achieved = graphene.Date()
    description = graphene.String()
    upload = graphene.Upload()
    thumbnail = graphene.Upload()
    slug = graphene.String()
    
    
class AwardsInputType(graphene.InputType):
    talent = graphene.Field(UserInputType)
    award = graphene.String()
    date_achieved = graphene.Date()
    description = graphene.String()
    tag = graphene.List(SkillTagInputType)
    upload = graphene.Upload()
    thumbnail = graphene.Upload()
    slug = graphene.String()
    
    
class PublicationsInputType(graphene.InputType):
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
    upload = graphene.Upload()
    slug = graphene.String()
    
    
class ResultInputType(graphene.InputType):
    type = graphene.String()
    
    
class CourseTypeInputType(graphene.InputType):
    type = graphene.String()
    
    
class LicenseCertificationInputType(graphene.InputType):
    talent = graphene.Field(UserInputType)
    certification = graphene.()
    cert_name = graphene.String()
    country = CountryFieldInputType(required=True)
    region = graphene.Field(RegionInputType)
    cm_no = graphene.String()
    companybranch = graphene.Field(EnterpriseInputType)
    upload = graphene.Upload()
    issue_date = graphene.Date()
    expiry_date = graphene.Date()
    current = graphene.Boolean()
    slug = graphene.String()
    
    
class CourseInputType(graphene.InputType):
    name = graphene.String()
    company = graphene.Field(EnterpriseInputType)
    course_type = graphene.Field(CourseTypeInputType)
    website = graphene.String()
    certification = graphene.Field(ResultInputType)
    
    
class TopicInputType(graphene.InputType):
    topic = graphene.String()
    skills = graphene.List(SkillTagInputType)
    hours = graphene.Decimal()
    
    
class LecturerInputType(graphene.InputType):
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
    
    
class ClassMatesInputType(graphene.InputType):
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
    
    
class DesignationInputType(graphene.InputType):
    name = graphene.String()
    
    
class WorkExperienceInputType(graphene.InputType):
    talent = graphene.Field(UserInputType)
    date_from = graphene.Date()
    date_to = graphene.Date()
    date_captured = graphene.Date()
    upload = graphene.Upload()
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
    
    
class WorkColleagueInputType(graphene.InputType):
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
    
    
class SuperiorInputType(graphene.InputType):
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
    
    
class WorkCollaboratorInputType(graphene.InputType):
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
    
    
class WorkClientInputType(graphene.InputType):
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
    
    
class EmailRemindValidateInputType(graphene.InputType):
    sender = graphene.Field(UserInputType)
    recipient = graphene.Field(UserInputType)
    subject = graphene.String()
    message = graphene.String()
    date_sent = graphene.DateTime()