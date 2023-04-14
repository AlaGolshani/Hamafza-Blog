from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe


class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    bio = models.TextField(max_length=400, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='authors/', blank=True, null=True)

    def image_tag(self):
        from django.utils.html import escape
        return mark_safe('<img src="/media/%s" width="80" height="80" />' % self.image)

    image_tag.short_description = 'Image'

    def __str__(self):
        return self.user.get_username()

