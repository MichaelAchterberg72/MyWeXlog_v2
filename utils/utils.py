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
            
            
def handle_m2m_relationship(instance, related_models_data):
    for field_name, (related_model, data, related_fields) in related_models_data.items():
        related_instances = []

        for item in data:
            filter_fields = {}
            create_fields = {}

            for related_field in related_fields:
                field_value = item.get(related_field, "").strip()
                filter_fields[f"{related_field}__iexact"] = field_value
                create_fields[related_field] = field_value

            related_instance, _ = related_model.objects.get_or_create(
                defaults=create_fields, **filter_fields
            )
            related_instances.append(related_instance)

        m2m_field = instance._meta.get_field(field_name)
        m2m_manager = getattr(instance, m2m_field.name)
        m2m_manager.set(related_instances)

    instance.save()
    
    
def create_enum_from_choices(choices):
    enum_values = {item[1]: item[0] for item in choices}
    return graphene.Enum.from_enum(enum.Enum("ChoicesEnum", enum_values))

