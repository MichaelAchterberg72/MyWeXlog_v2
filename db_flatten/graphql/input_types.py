import graphene


class PhoneNumberTypeInputType(graphene.InputObjectType):
    type = graphene.String()
    
    
class SkillTagInputType(graphene.InputObjectType):
    skill = graphene.String()
    code = graphene.String()
    
    
class LanguageListInputType(graphene.InputObjectType):
    language = graphene.String()