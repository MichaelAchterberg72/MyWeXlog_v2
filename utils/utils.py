import enum
import graphene
from django.db.models.fields.related import RelatedField


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
    enum_values = {item[1]: item[0] for item in choices}
    return graphene.Enum.from_enum(enum.Enum("ChoicesEnum", enum_values))

