from django.contrib import admin

from apps.articles.models import Post, Badge, Image


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'author',
        'publish_status',
        'publish_date',
        'image_tag', ]
    list_display_links = ['title']
    list_editable = [
        'publish_status',
        'publish_date']
    inlines = [ImageInline]
    fields = ['title',
              'author',
              ('publish_status', 'publish_date'),
              ('badges', 'image'),
              'created_on',
              'updated_on',
              'content',
    ]
    readonly_fields = [
        'created_on',
        'updated_on',
    ]
    sortable_by = [
        'title',
        'author',
        'publish_date'
    ]
    list_filter = [
        'badges',
        'publish_status'
    ]
    search_fields = (
        "title",
        "content",
    )
    date_hierarchy = "publish_date"
