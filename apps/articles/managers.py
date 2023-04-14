import datetime

from django.db.models import Manager


class PostManager(Manager):
    def published(self):
        return self.filter(
            publish_date__lte=datetime.datetime.now(),
            publish_status='P'
        )
