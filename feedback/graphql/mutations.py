import graphene
from django.db import transaction

from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult
from utils.utils import update_or_create_object

from .input_types import (
    FeedbackInputType,
    FeedBackActionsInputType,
    NoticesInputType,
    NoticeReadInputType
)

from ..models import (
    FeedBack,
    FeedBackActions,
    Notices,
    NoticeRead
)


class FeedbackUpdateOrCreate(graphene.Mutation):
    class Arguments:
        id = FeedbackInputType.id
        talent = FeedbackInputType.talent
        date_captured = FeedbackInputType.date_captured
        type = FeedbackInputType.type
        details = FeedbackInputType.details
        optional_1 = FeedbackInputType.optional_1
        optional_2 = FeedbackInputType.optional_2
        responded = FeedbackInputType.responded
        slug = FeedbackInputType.slug
        
    Output = SuccessMutationResult
        
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                feedback_id = kwargs.get('id')
                feedback = update_or_create_object(FeedBack, kwargs)
                message = "Feedback updated successfully" if feedback_id else "Feedback created successfully"
                return SuccessMessage(success=True, id=feedback.id, message=message)
        except Exception as e:
            return FailureMessage(success=False, message=f"Error adding feedback", errors=[str(e)])


class FeedbackDelete(graphene.Mutation):
    class Arguments:
        id = FeedbackInputType.id
        
    Output = SuccessMutationResult
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        errors = []
        if errors:
            return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
        
        try:
            with transaction.atomic():
                feedback = FeedBack.objects.get(kwargs['id']).delete()
                return SuccessMessage(success=True, id=kwargs['id'], message="Feedback deleted successfully")
        except Exception as e:
            return FailureMessage(success=False, message=f"Error deleting feedback", errors=[str(e)])



class Mutation(graphene.ObjectType):
    feedback_update_or_create = FeedbackUpdateOrCreate.Field()
    feedback_delete = FeedbackDelete.Field()


# # Validation functions
# def validate_model1_input(input):
#     validation_errors = []

#     # Perform validations specific to Model1 input
#     if input.get('field1') is None:
#         validation_errors.append('Field1 is required.')

#     # Add more validations...

#     return validation_errors

# def validate_model2_input(input):
#     validation_errors = []

#     # Perform validations specific to Model2 input
#     if input.get('field2') is None:
#         validation_errors.append('Field2 is required.')
        
        


# # Generate mutations for specific models in an app
# app_name = 'feedback'
# model_names = ['FeedBack', 'FeedBackActions', 'Notices', 'NoticeRead']
# mutation_name_format = '{model}_update_or_create'
# output_message_format = "{model} {action} successfully"
# delete_mutation_name_format = '{model}_delete'
# delete_output_message_format = "{model} deleted successfully"
# validation_functions = [validate_model1_input, validate_model2_input]
# related_model_map = {
#     'CustomUser': CustomUser,
# }
# # validation_functions = []

# mutations = create_mutations_for_app(
#     app_name, 
#     model_names, 
#     mutation_name_format, 
#     output_message_format, 
#     validation_func=validation_functions
#     )
# delete_mutations = create_delete_mutation_for_app(app_name, model_names)

# class Mutation(graphene.ObjectType):
#     # Custom mutations
#     class Meta:
#         mutation_classes = mutations + delete_mutations
        
# # Add the generated mutations to the Mutation class
# for mutation in mutations + delete_mutations:
#     setattr(Mutation, mutation.__name__, mutation)
    # my_custom_mutation = MyCustomMutation.Field()
# Add the generated mutations to the Mutation class
# for mutation in mutations:
#     print(mutation.__name__)
#     setattr(Mutation, mutation.__name__, mutation)
    
    
# for mutation in delete_mutations:
#     setattr(Mutation, mutation.__name__, mutation)