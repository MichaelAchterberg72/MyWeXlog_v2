import graphene


class PhoneNumberTypeInputType(graphene.InputObjectType):
    id = graphene.ID()
    type = graphene.String()
    
    
class SkillTagInputType(graphene.InputObjectType):
    id = graphene.ID()
    skill = graphene.String()
    code = graphene.String()
    
    
class LanguageListInputType(graphene.InputObjecttype):
    id = graphene.ID()
    language = graphene.String()