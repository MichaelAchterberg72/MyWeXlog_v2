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

def handle_achievements(obj_model, achievements):
    if obj_model is not None:
        achievements_obj = Achievements.objects.get(
            id=achievements.id or obj_model.achievements.id,
        )
        achievements_obj.achievement = (
            achievements.achievement
            if achievements.achievement is not None
            else achievements_obj.achievement
        )
        achievements_obj.date_achieved = (
            achievements.date_achieved
            if achievements.date_achieved is not None
            else achievements_obj.date_achieved
        )
        achievements_obj.description = (
            achievements.description
            if achievements.description is not None
            else achievements_obj.description
        )
        achievements_obj.upload = (
            achievements.upload
            if achievements.upload is not None
            else achievements_obj.upload
        )
        
    else:
        achievements_obj = Achievements.objects.create(
            talent = achievements.talent
            if achievements.talent is not None
            else None
            
            achievement = achievements.achievement
            if achievements.achievement is not None
            else None
            
            date_achieved = achievements.date_achieved
            if achievements.date_achieved is not None
            else None
            
            description = achievements.description
            if achievements.description is not None
            else None
            
            upload = achievements.upload
            if achievements.upload is not None
            else None
        )
    obj_model.achievements = achievements_obj
    obj_model.save()
    
    return obj_model


def handle_awards(obj_model, awards):
    if obj_model is not None:
        awards_obj = Awards.objects.get(
            id=awards.id or obj_model.awards.id
        )
        awards_obj.talent = (
            awards.talent
            if awards.talent is not None
            else awards_obj.talent
        )
        awards_obj.award = (
            awards.award
            if awards.award is not None
            else awards_obj.award
        )
    else:
        awards_obj = Awards.objects.create(
            talent = awards.talent
            if awards.talent is not None
            else None
        )
        
    obj_model.awards = awards_obj
    obj_model.save()
        