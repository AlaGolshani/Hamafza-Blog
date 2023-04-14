import graphene
from django.db.models import Q
from django.shortcuts import get_object_or_404
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required

from .models import Post, Badge, Image
from ..accounts.models import AuthorProfile


class PostType(DjangoObjectType):
    class Meta:
        model = Post


class BadgeType(DjangoObjectType):
    class Meta:
        model = Badge


class ImageType(DjangoObjectType):
    class Meta:
        model = Image


class ArticlesQuery(graphene.ObjectType):
    # badges query
    badges = graphene.List(BadgeType, name=graphene.String())

    # posts query
    posts = graphene.List(PostType, title=graphene.String())
    posts_by_content = graphene.List(PostType,
                                     content=graphene.String(required=True))
    posts_by_publish_date = graphene.List(PostType,
                                          publish_date=graphene.Date(required=True))
    posts_by_author_name = graphene.List(PostType,
                                         author_name=graphene.String(required=True))
    posts_by_badges = graphene.List(PostType, badge_names=graphene.List(graphene.String))

    @staticmethod
    def resolve_badges(parent, info, **kwargs):
        name = kwargs.get('name')
        if name is not None:
            return Badge.objects.filter(name__icontains=name)
        return Badge.objects.all()

    @staticmethod
    def resolve_posts(parent, info, **kwargs):
        title = kwargs.get('title')
        if title is not None:
            return Post.objects.published().filter(title__icontains=title)
        return Post.objects.published()

    @staticmethod
    def resolve_posts_by_content(parent, info, **kwargs):
        content = kwargs.get('content')
        if content is not None:
            posts = Post.objects.published().filter(content__icontains=content)
            return posts
        return None

    @staticmethod
    def resolve_posts_by_publish_date(parent, info, **kwargs):
        publish_date = kwargs.get('publish_date')
        if publish_date is not None:
            posts = Post.objects.published().filter(publish_date=publish_date)
            return posts
        return None

    @staticmethod
    def resolve_posts_by_author_name(parent, info, **kwargs):
        author_name = kwargs.get('author_name')
        if author_name is not None:
            posts = Post.objects.published().filter(
                Q(author__user__username__icontains=author_name) |
                Q(author__user__first_name__icontains=author_name) |
                Q(author__user__last_name__icontains=author_name))
            return posts
        return None

    @staticmethod
    def resolve_posts_by_badges(parent, info, **kwargs):
        badge_names = kwargs.get('badge_names')
        badges_post = {}
        for badge_name in badge_names:
            posts = set(Post.objects.filter(badges__name__in=[badge_name]))
            badges_post[badge_name] = posts
        common_posts = set.intersection(*badges_post.values())
        return common_posts


class PostInput(graphene.InputObjectType):
    title = graphene.String()
    content = graphene.String()
    author_username = graphene.String()
    publish_status = graphene.String()
    publish_date = graphene.Date()
    badges_name = graphene.List(graphene.String)
    image = Upload(required=False)


class CreatePost(graphene.Mutation):
    class Arguments:
        input = PostInput()

    post = graphene.Field(PostType)
    ok = graphene.Boolean(default_value=False)

    @staticmethod
    @login_required
    def mutate(parent, info, input=None):
        badges_list = []
        if input.badges_name is not None:
            for badge_name in input.badges_name:
                badge = Badge.objects.get(name__iexact=badge_name)
                badges_list.append(badge)

        author_instance = AuthorProfile.objects.get(user__username=input.author_username)

        post_instance = Post.objects.create(
            title=input.title,
            content=input.content,
            author=author_instance
        )
        if input.publish_status:
            post_instance.publish_status = input.publish_status
        if input.publish_date:
            post_instance.publish_date = input.publish_date
        if input.image:
            post_instance.image = input.image
        post_instance.badges.set(badges_list)
        ok = True
        return CreatePost(post=post_instance, ok=ok)


class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PostInput()

    post = graphene.Field(PostType)
    ok = graphene.Boolean(default_value=False)

    @staticmethod
    @login_required
    def mutate(parent, info, id, input=None):
        post_instance = Post.objects.get(id=id)
        ok = False

        if info.context.user == post_instance.author.user:
            if input.author_username:
                post_instance.author.user.username = input.author_username
            if input.title:
                post_instance.title = input.title
            if input.content:
                post_instance.content = input.content
            if input.publish_status:
                post_instance.publish_status = input.publish_status
            if input.publish_date:
                post_instance.publish_date = input.publish_date
            if input.image:
                post_instance.image = input.image
            if input.badges_name:
                badges_list = []
                for badge_name in input.badges_name:
                    badge = Badge.objects.get(name__iexact=badge_name)
                    badges_list.append(badge)
                post_instance.badges.set(badges_list)
            ok = True

        post_instance.save()
        post_instance.author.user.save()

        return CreatePost(post=post_instance, ok=ok)


class DeletePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int(required=True)

    post = graphene.Field(PostType)
    ok = graphene.Boolean(default_value=False)

    @staticmethod
    @login_required
    def mutate(parent, info, post_id):
        post_instance = get_object_or_404(Post, id=post_id)
        ok = False
        if info.context.user == post_instance.author.user:
            post_instance.delete()
            ok = True
        return CreatePost(post=post_instance, ok=ok)


class ArticleMutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
