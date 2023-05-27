import graphene

from django.db.models import Q, Sum

import allauth.graphql.queries
import billing.graphql.queries
import booklist.graphql.queries
import db_flatten.graphql.queries
import enterprises.graphql.queries
import feedback.graphql.queries
import users.graphql.queries

# import allauth.graphql.mutations
import allauth.graphql.jwt_mutations
import billing.graphql.mutations
import booklist.graphql.mutations 
import db_flatten.graphql.mutations 
import enterprises.graphql.mutations 
import feedback.graphql.mutations

import graphql_jwt


class Query(
    allauth.graphql.queries.Query, 
    billing.graphql.queries.Query,
    booklist.graphql.queries.Query,
    db_flatten.graphql.queries.Query,
    enterprises.graphql.queries.Query,
    feedback.graphql.queries.Query,
    users.graphql.queries.Query,
    
    graphene.ObjectType
):
    pass
    # usr = graphene.Field(graphene.ID)


class Mutation(
    # allauth.graphql.mutations.Mutation, 
    allauth.graphql.jwt_mutations.Mutation,
    billing.graphql.mutations.Mutation,
    booklist.graphql.mutations.Mutation, 
    db_flatten.graphql.mutations.Mutation,   
    enterprises.graphql.mutations.Mutation,
    feedback.graphql.mutations.Mutation,
    graphene.ObjectType
):
    # token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    

# print(dir(Mutation))
schema = graphene.Schema(query=Query, mutation=Mutation)
# schema_str = str(schema)
# print(schema_str)