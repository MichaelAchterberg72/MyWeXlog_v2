import sys
import enum
import graphene
from django.db import models, transaction
from django.apps import apps
from django.db import transaction, IntegrityError
import random
import string
from django.db.models.fields.related import RelatedField
from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult
from django.db import IntegrityError
from django.conf import settings

# from django.contrib.auth import get_user_model
# from users.models import CustomUser as User

# User = get_user_model()


def update_model(model, **kwargs):
    for attr, value in kwargs.items():
        if attr == "id":
            pass  # pass, do not modify primary key
        else:
            exists = hasattr(model, attr)
            if exists and not isinstance(getattr(model, attr), RelatedField):
                setattr(model, attr, value)
        if attr == "password":
            model.set_password(value)
            
            
def update_or_create_related_object(model_class, data):
    obj_id = data.pop('id', None)
    if obj_id:
        obj = model_class.objects.filter(id=obj_id).first()
        if obj:
            update_model(obj, **data)
            obj.save()
            return obj
        else:
            raise ValueError(f"{model_class.__name__} with id={obj_id} does not exist.")
    else:
        return model_class.objects.update_or_create(**data)[0]
    
    
def handle_m2m_relationship(obj, related_models_data_list):
    for related_models_data in related_models_data_list:
        model = related_models_data['model']
        manager_name = related_models_data['manager']
        fields = related_models_data['fields']
        data_list = related_models_data['data']

        related_manager = getattr(obj, manager_name)

        for related_data in data_list: 
            filter_kwargs = {field: related_data.get(field) for field in fields if field != 'id'}
            related_instance_id = related_data.get('id')
            
            if related_instance_id:
                related_instance = model.objects.filter(id=related_instance_id).first()
                if related_instance:
                    related_manager.add(related_instance)
            else:                    
                related_instance, created = model.objects.get_or_create(**filter_kwargs)
                related_manager.add(related_instance)

    return obj


# @classmethod
def update_or_create_object(model, data, related_model_map=None):
    print("############1############")
    obj_id = data.pop('id', None)
    m2m_fields = {}
    foreign_key_fields = {}
    regular_fields = {}
    for field, value in data.items():
        if isinstance(value, list):
            m2m_fields[field] = value
        elif isinstance(value, dict):
            foreign_key_fields[field] = value
        else:
            regular_fields[field] = value
    print("############2############")
    obj = None
    if obj_id:
        obj = model.objects.filter(id=obj_id).first()
        if obj:
            for field, value in regular_fields.items():
                setattr(obj, field, value)
            obj.save()
    print("############3############")
    if not obj:
        if regular_fields:
            # Exclude m2m fields and foreign key fields from create() kwargs
            create_kwargs = {key: value for key, value in regular_fields.items() if key not in m2m_fields and key not in foreign_key_fields}
            try:
                obj = model.objects.create(**create_kwargs)
            except IntegrityError:
                pass
        else:
            return None
    print("############4############")
    if foreign_key_fields:
        for field, value in foreign_key_fields.items():
            related_model = getattr(model, field).field.related_model
            related_obj_id = value.pop('id', None)
            related_obj_slug = value.pop('slug', None)
                
            field_obj = model._meta.get_field(field)
            if related_model_map and related_model.__name__ in related_model_map:
                related_model = related_model_map[related_model.__name__]
                
            if related_model.__name__ == apps.get_model('users', 'CustomUser').__name__:
                if 'alias' in value:
                    related_obj = related_model.objects.filter(alias=value['alias']).first()
                    setattr(obj, field, related_obj)
                continue
            
            if not related_model.__name__ == apps.get_model('users', 'CustomUser').__name__:
                if related_obj_id:
                    related_obj = related_model.objects.filter(id=related_obj_id).first()
                    if related_obj:
                        setattr(obj, field, related_obj)
                elif related_obj_slug:
                    related_obj = related_model.objects.filter(slug=related_obj_slug).first()
                    if related_obj:
                        setattr(obj, field, related_obj)
                else:
                    related_obj = model.update_or_create_object(related_model, value, related_model_map=related_model_map)
                    if related_obj is not None:
                        for fk_field in field_obj.foreign_related_fields:
                            setattr(related_obj, fk_field.name, obj)
                            setattr(obj, fk_field.name, related_obj)
                        related_obj.save()
                    setattr(obj, field, related_obj)
    print("############5############")
    if m2m_fields:
        for field, value in m2m_fields.items():
            m2m_related_models_data = {
                'model': getattr(model, field).field.related_model,
                'manager': field,
                'fields': [f.name for f in getattr(model, field).field.related_model._meta.fields],
                'data': value,
            }
            model = m2m_related_models_data['model']
            manager_name = m2m_related_models_data['manager']
            fields = m2m_related_models_data['fields']
            data_list = m2m_related_models_data['data']

            related_manager = getattr(obj, manager_name)

            for related_data in data_list: 
                filter_kwargs = {field: related_data.get(field) for field in fields if field != 'id'}
                related_instance_id = related_data.get('id')
                
                if related_instance_id:
                    related_instance = model.objects.filter(id=related_instance_id).first()
                    if related_instance:
                        related_manager.add(related_instance)
                else:                    
                    related_instance, created = model.objects.get_or_create(**filter_kwargs)
                    related_manager.add(related_instance)
    print("############6############")
    if obj:
        obj.save()
    print("############7############")
    return obj


def create_enum_from_choices(choices):
    enum_values = {item[0]: item[1] for item in choices}
    enum_name = 'ChoicesEnum_' + ''.join([str(value) for value in enum_values.values()])
    ChoicesEnum = enum.Enum(enum_name, enum_values)
    return graphene.Enum.from_enum(ChoicesEnum)


# class CustomUserForeignKeyInput(graphene.InputObjectType):
#     alias = graphene.String(required=True)

# input_type_cache = {}

# def get_input_type_for_model(model):
#     if model in input_type_cache:
#         return input_type_cache[model]
    
#     fields = {}
#     for field in model._meta.get_fields():
#         if isinstance(field, models.CharField) or isinstance(field, models.TextField) or isinstance(field, models.EmailField):
#             fields[field.name] = graphene.String(required=not field.blank)
#         elif isinstance(field, models.IntegerField):
#             fields[field.name] = graphene.Int(required=not field.blank)
#         elif isinstance(field, models.BooleanField):
#             fields[field.name] = graphene.Boolean(required=not field.blank)
#         elif isinstance(field, models.FloatField):
#             fields[field.name] = graphene.Float(required=not field.blank)
#         elif isinstance(field, models.DecimalField):
#             fields[field.name] = graphene.Decimal(required=not field.blank)
#         elif isinstance(field, models.DateField):
#             fields[field.name] = graphene.Date(required=not field.blank)
#         elif isinstance(field, models.DateTimeField):
#             fields[field.name] = graphene.DateTime(required=not field.blank)
#         if isinstance(field, models.ForeignKey):
#             if field.related_model != apps.get_model('users', 'CustomUser'):  # Exclude User model
#                 related_model_input_type = get_input_type_for_model(field.related_model)
#                 fields[field.name] = graphene.Field(related_model_input_type, required=not field.blank)
#             else:
#                 fields[field.name] = graphene.Field(CustomUserForeignKeyInput, required=not field.blank)
#         if isinstance(field, models.ManyToManyField):
#             if field.related_model != apps.get_model('users', 'CustomUser').__name__:  # Exclude User model
#                 # To allow creating new related instances, generate an InputObjectType for the related model:
#                 related_model_input_type = get_input_type_for_model(field.related_model)
#                 fields[field.name] = graphene.List(graphene.NonNull(related_model_input_type), required=not field.blank)
#             else:
#                 related_model_input_type = get_input_type_for_model(field.related_model)
#                 fields[field.name] = graphene.List(graphene.NonNull(related_model_input_type), required=not field.blank)

#     Meta = type('Meta', (object,), {'model': model})
#     input_type = type(model.__name__ + 'InputType', (graphene.InputObjectType,), fields)
#     input_type.Meta = Meta

#     input_type_cache[model] = input_type

#     return input_type


# def create_mutations_for_app(
#     app_name, 
#     model_names, 
#     mutation_name_format, 
#     output_message_format, 
#     related_model_map=None, 
#     validation_func_map=None,
#     model=None
# ):
#     app = apps.get_app_config(app_name)
#     mutations = []
#     mutation_map = {}

#     for model in app.get_models():
#         if model.__name__ in model_names:
#             ModelInputType = get_input_type_for_model(model)

#             class UpdateOrCreateModelMutation(graphene.Mutation):
#                 class Arguments:
#                     input = ModelInputType(required=True)

#                 Output = SuccessMutationResult

#                 @classmethod
#                 def mutate(cls, root, info, input):
#                     if validation_func_map and model.__name__ in validation_func_map:
#                         validation_func = validation_func_map[model.__name__]
#                         errors = validation_func(input)
#                         if errors:
#                             return FailureMessage(success=False, message=f"There are validation errors", errors=errors)
#                     try:
#                         with transaction.atomic():
#                             model_instance = update_or_create_object(model, input, related_model_map=related_model_map)
#                             if model_instance:
#                                 output_message = output_message_format.format(model=model.__name__, id=model_instance.id)
#                                 return SuccessMessage(success=True, id=str(model_instance.id), message=output_message)
#                     except Exception as e:
#                         return FailureMessage(success=False, message=f"Error creating or updating {model.__name__}", errors=[str(e)])

#             mutation_name = mutation_name_format.format(model=model.__name__)
#             UpdateOrCreateModelMutation.__name__ = mutation_name
#             mutations.append(UpdateOrCreateModelMutation)
#             mutation_map[mutation_name] = UpdateOrCreateModelMutation

#     return mutations, mutation_map


# def create_delete_mutation_for_app(app_name, model_names):
#     app = apps.get_app_config(app_name)
#     mutations = []
#     mutation_map = {}

#     for model in app.get_models():
#         if model.__name__ in model_names:
#             class DeleteMutation(graphene.Mutation):
#                 class Arguments:
#                     id = graphene.ID(required=True)

#                 Output = SuccessMutationResult

#                 @classmethod
#                 def mutate(cls, root, info, id):
#                     try:
#                         with transaction.atomic():
#                             model_instance = model.objects.get(id=id)
#                             model_instance.delete()
#                             return SuccessMessage(success=True, id=str(id), message="Object deleted successfully")
#                     except Exception as e:
#                         return FailureMessage(success=False, message=f"Error deleting object", errors=[str(e)])

#             mutation_name = f"{model.__name__}Delete"
#             DeleteMutation.__name__ = mutation_name
#             # setattr(sys.modules[__name__], mutation_name, DeleteMutation)
#             # mutations.append(DeleteMutation)

#             mutations.append(DeleteMutation)
#             mutation_map[mutation_name] = DeleteMutation
#     return mutations, mutation_map
