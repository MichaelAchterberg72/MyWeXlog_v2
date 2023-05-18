import graphene
from utils.utils import create_mutations_for_app

from ..models import (
    FeedBack,
    FeedBackActions,
    Notices,
    NoticeRead
)

# Validation functions
def validate_model1_input(input):
    validation_errors = []

    # Perform validations specific to Model1 input
    if input.get('field1') is None:
        validation_errors.append('Field1 is required.')

    # Add more validations...

    return validation_errors

def validate_model2_input(input):
    validation_errors = []

    # Perform validations specific to Model2 input
    if input.get('field2') is None:
        validation_errors.append('Field2 is required.')
        
        
class Mutation(graphene.ObjectType):
    # Custom mutations
    my_custom_mutation = MyCustomMutation.Field()

# Generate mutations for specific models in an app
app_name = 'feedback'
model_names = ['FeedBackActions', 'Notices']
mutation_name_format = '{model}UpdateOrCreate'
validation_functions = [validate_model1_input, validate_model2_input]

mutations = create_mutations_for_app(app_name, model_names, mutation_name_format, validation_functions)

# Add the generated mutations to the Mutation class
for mutation in mutations:
    setattr(Mutation, mutation.__name__, mutation)