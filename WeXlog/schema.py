import graphene
from django.db.models import Q, Sum

import allauth.graphql.queries
import booklist.graphql.queries 

# import allauth.graphql.mutations
import booklist.graphql.mutations 
import allauth.graphql.jwt_mutations
import booklist

import graphql_jwt


class Query(
    allauth.graphql.queries.Query, 
    booklist.graphql.queries.Query,
    graphene.ObjectType
):
    pass


class Mutation(
    # allauth.graphql.mutations.Mutation, 
    allauth.graphql.jwt_mutations.Mutation,
    booklist.graphql.mutations.Mutation,    
    graphene.ObjectType
):
    # token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)