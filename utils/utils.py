import enum
import graphene
import random
import string
from graphene import relay
from django.db.models.fields.related import RelatedField
from utils.graphql.output_types import SuccessMessage, FailureMessage, SuccessMutationResult
from django.db import IntegrityError
from django.conf import settings

from django.contrib.auth import get_user_model

User = get_user_model()


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


@classmethod
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
            for field, value in regular_fields.items():
                setattr(obj, field, value)
            obj.save()

    if not obj:
        from django.db import IntegrityError

        if regular_fields:
            # Exclude m2m fields and foreign key fields from create() kwargs
            create_kwargs = {key: value for key, value in regular_fields.items() if key not in m2m_fields and key not in foreign_key_fields}
            try:
                obj = model.objects.create(**create_kwargs)
            except IntegrityError:
                pass
        else:
            return None
        
    if foreign_key_fields:
        for field, value in foreign_key_fields.items():
            related_model = getattr(model, field).field.related_model
            related_obj_id = value.pop('id', None)
            
            if related_model == User:
                related_obj = User.objects.filter(pk=related_obj_id).first()
                obj.related_obj = related_obj
                
            field_obj = model._meta.get_field(field)
            if related_obj_id:
                related_obj = related_model.objects.filter(id=related_obj_id).first()
                if related_obj:
                    setattr(obj, field, related_obj)
            else:
                related_obj = model.update_or_create_object(related_model, value)
                if related_obj is not None:
                    for fk_field in field_obj.foreign_related_fields:
                        setattr(related_obj, fk_field.name, obj)
                setattr(obj, field, related_obj)

    if m2m_fields:
        m2m_related_models_data_list = []
        for field, value in m2m_fields.items():
            m2m_related_models_data = {
                'model': getattr(model, field).field.related_model,
                'manager': field,
                'fields': [f.name for f in getattr(model, field).field.related_model._meta.fields],
                'data': value,
            }
            m2m_related_models_data_list.append(m2m_related_models_data)
        
        # Call the handle_m2m_relationship method on the class (model)
        handle_m2m_relationship(obj, m2m_related_models_data_list)

    if obj:
        obj.save()
        
    return obj


def create_enum_from_choices(choices):
    enum_values = {item[0]: item[1] for item in choices}
    enum_name = 'ChoicesEnum_' + ''.join([str(value) for value in enum_values.values()])
    ChoicesEnum = enum.Enum(enum_name, enum_values)
    return graphene.Enum.from_enum(ChoicesEnum)