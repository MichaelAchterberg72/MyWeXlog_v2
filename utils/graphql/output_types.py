import graphene


class SuccessMessage(graphene.ObjectType):
    id = graphene.ID()
    success = graphene.Boolean()
    message = graphene.String()
    
    
class FailureMessage(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    
    
class SuccessMutationResult(graphene.Union):
    class Meta:
        types = (SuccessMessage, FailureMessage)