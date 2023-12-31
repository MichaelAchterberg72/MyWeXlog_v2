import graphene


class UserInputType(graphene.InputObjectType):
    username = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()
    is_staff = graphene.String()
    is_active = graphene.String()
    date_joined = graphene.String()
    alias = graphene.String()
    display_text = graphene.String()
    public_profile_name = graphene.String()
    permit_viewing_of_profile_as_reference = graphene.Boolean()
    subscription = graphene.Int()
    permission = graphene.Int()
    role = graphene.Int()
    registered_date = graphene.DateTime()
    paid = graphene.Boolean()
    free_month = graphene.Boolean()
    paid_date = graphene.DateTime()
    paid_type = graphene.Int()
    invite_code = graphene.String()
    alphanum = graphene.String()