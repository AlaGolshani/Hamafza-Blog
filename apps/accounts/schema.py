import graphene
import graphql_jwt
from django.contrib.auth.models import User
from django.db.models import Q, Count
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from django.shortcuts import get_object_or_404
from graphql_jwt.decorators import login_required

from .models import AuthorProfile
from ..articles.models import Post


class AuthorType(DjangoObjectType):
    class Meta:
        model = AuthorProfile


class UserType(DjangoObjectType):
    class Meta:
        model = User


class AuthorQuery(graphene.ObjectType):
    the_author = graphene.Field(AuthorType)
    authors = graphene.List(
        AuthorType,
        name=graphene.String())
    author_by_articles_number = graphene.List(
        AuthorType,
        number=graphene.Int(required=True))
    author_by_article_badges = graphene.List(
        AuthorType,
        badge_names=graphene.List(graphene.String))

    @staticmethod
    def resolve_the_author(parent, info, **kwargs):
        return AuthorProfile.objects.get(user=info.context.user)

    @staticmethod
    def resolve_authors(parent, info, **kwargs):
        name = kwargs.get('name')
        if name is not None:
            return AuthorProfile.objects.filter(
                Q(user__first_name__icontains=name) |
                Q(user__last_name__icontains=name)
            )
        return AuthorProfile.objects.all()

    @staticmethod
    def resolve_author_by_articles_number(parent, info, **kwargs):
        number = kwargs.get('number')
        if number is not None:
            authors = AuthorProfile.objects \
                .annotate(num_articles=Count('posts')) \
                .filter(num_articles=number)
            return authors
        return None

    @staticmethod
    def resolve_author_by_article_badges(parent, info, **kwargs):
        badge_names = kwargs.get('badge_names')
        badges_articles = {}
        for badge_name in badge_names:
            posts = set(Post.objects.filter(badges__name__in=[badge_name]))
            authors = set()
            for post in posts:
                authors.add(post.author)
            badges_articles[badge_name] = authors
        common_posts = set.intersection(*badges_articles.values())
        return common_posts


class AuthorInput(graphene.InputObjectType):
    bio = graphene.String()
    age = graphene.Int()
    image = Upload(required=False)


class UpdateAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = AuthorInput()

    author = graphene.Field(AuthorType)
    ok = graphene.Boolean(default_value=False)

    @staticmethod
    @login_required
    def mutate(parent, info, id, input=None):
        ok = False
        author_instance = get_object_or_404(AuthorProfile, pk=id)
        if info.context.user == author_instance.user:
            if input.bio:
                author_instance.bio = input.bio
            if input.age:
                author_instance.age = input.age
            if input.image:
                author_instance.image = input.image
            author_instance.save()
            ok = True
        return UpdateAuthor(author=author_instance, ok=ok)


class AuthorMutation(graphene.ObjectType):
    update_author = UpdateAuthor.Field()
    login_token = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
