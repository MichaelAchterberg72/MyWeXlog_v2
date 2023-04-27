import graphene


class SaveContentSuccess(graphene.ObjectType):
    id = graphene.ID(required=True)
    message = graphene.String(required=True)
    
    
class SaveContentFailure(graphene.ObjectType):
    message = graphene.String(required=True)