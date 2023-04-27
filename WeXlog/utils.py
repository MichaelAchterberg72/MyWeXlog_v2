

def update_model(model, **kwargs):
    for name, value in kwargs.items():
        if name == "id" or name == "material_code" or name == "custom_material_code":
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
    
    
# # Get an existing Awards instance
# award = Awards.objects.get(pk=award_id)

# # Provide a dictionary containing related models, data, and related field names
# related_models_data = {
#     'tag': (SkillTag, [{"skill": "Skill 1"}, {"skill": "Skill 2"}], ["skill"]),
#     # You can add other ManyToManyFields with their related models, data, and related field names here
# }

# # Update the ManyToManyFields for the award
# handle_m2m_relationship(instance=award, related_models_data=related_models_data)

