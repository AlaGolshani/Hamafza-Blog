from django.utils.safestring import mark_safe
from django.db import models

from .managers import PostManager
from ..accounts.models import AuthorProfile


class Badge(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    DRAFT = 'D'
    RELEASE = 'P'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (RELEASE, 'Publish'),
    ]

    title = models.CharField(max_length=150)
    content = models.TextField()
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.PROTECT,
        related_name='posts',
    )
    publish_status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=DRAFT,
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    publish_date = models.DateField(blank=True, null=True)
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )
    badges = models.ManyToManyField(Badge, related_name='posts',
                                    blank=True)
    objects = PostManager()

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="100" height="100" />' % self.image)

    image_tag.short_description = 'Image'

    def __str__(self):
        return self.title


class Image(models.Model):
    image = models.ImageField(upload_to='posts/gallery')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images_gallery')
