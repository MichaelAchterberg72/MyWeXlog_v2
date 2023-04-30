import graphene


<<<<<<< HEAD
class SaveContentSuccess(graphene.ObjectType):
    id = graphene.ID(required=True)
    message = graphene.String(required=True)
    
    
class SaveContentFailure(graphene.ObjectType):
    message = graphene.String(required=True)
=======
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
>>>>>>> 2023-04-30-install-initial-graphql
