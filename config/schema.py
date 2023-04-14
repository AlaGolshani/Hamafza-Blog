import graphene

from apps.accounts.schema import AuthorQuery, AuthorMutation
from apps.articles.schema import ArticlesQuery, ArticleMutation


class Query(ArticlesQuery, AuthorQuery, graphene.ObjectType):
    pass


class Mutation(AuthorMutation, ArticleMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
