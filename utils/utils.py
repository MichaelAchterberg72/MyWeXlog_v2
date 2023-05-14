import enum
import graphene
import random
import string
from graphene import relay
from django.db.models.fields.related import RelatedField
from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult
from django.db import IntegrityError


def update_model(model, **kwargs):
    for name, value in kwargs.items():
        if name == "id":
            pass  # pass, do not modify primary key
        else:
            exists = hasattr(model, name)
            if exists and not isinstance(getattr(model, name), RelatedField):
                setattr(model, name, value)
        if name == "password":
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
    
            
def update_or_create_object(model, data):
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

    obj = None
    if obj_id:
        obj = model.objects.filter(id=obj_id).first()
        if obj:
            for field, value in m2m_fields.items():
                m2m_field = getattr(obj, field)
                m2m_field.set(value)
            for field, value in foreign_key_fields.items():
                related_model = getattr(model, field).related_model
                related_obj_id = value.pop('id', None)
                if related_obj_id:
                    related_obj = related_model.objects.filter(id=related_obj_id).first()
                    if related_obj:
                        setattr(obj, field, related_obj)
            for field, value in regular_fields.items():
                setattr(obj, field, value)
            obj.save()

    if not obj and regular_fields:
        obj = model.objects.create(**data)
        for field, value in m2m_fields.items():
            m2m_field = getattr(obj, field)
            m2m_field.set(value)
        for field, value in foreign_key_fields.items():
            related_model = getattr(model, field).related_model
            related_obj_id = value.pop('id', None)
            if related_obj_id:
                related_obj = related_model.objects.filter(id=related_obj_id).first()
                if related_obj:
                    setattr(obj, field, related_obj)
            else:
                related_obj = related_model.objects.create(**value)
                setattr(obj, field, related_obj)
        obj.save()

    return obj

            
def handle_m2m_relationship(instance, related_models_data_list):
    for related_models_data in related_models_data_list:
        model = related_models_data['model']
        manager_name = related_models_data['manager']
        fields = related_models_data['fields']

        related_manager = getattr(instance, manager_name)

        for related_data in related_models_data['data']:
            filter_kwargs = {field: related_data[field] for field in fields if related_data.get(field)} if fields else {}
            related_instance, created = model.objects.get_or_create(**filter_kwargs)

            if not related_manager.filter(id=related_instance.id).exists():
                related_manager.add(related_instance)

    return instance
    

def create_enum_from_choices(choices):
    enum_values = {item[0]: item[1] for item in choices}

    enum_name = 'ChoicesEnum_' + ''.join([str(value) for value in enum_values.values()])

    ChoicesEnum = enum.Enum(enum_name, enum_values)

    return graphene.Enum.from_enum(ChoicesEnum)