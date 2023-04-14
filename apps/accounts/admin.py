from django.contrib import admin

from apps.accounts.models import AuthorProfile
from apps.articles.models import Post


class PostInline(admin.TabularInline):
    model = Post
    extra = 1


@admin.register(AuthorProfile)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'age', 'image_tag']
    list_display_links = ['username']
    list_editable = ['age']

    def username(self, x):
        return x.user.username


