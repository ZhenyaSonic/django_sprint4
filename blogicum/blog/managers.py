from django.db import models
from django.utils import timezone


class PostManager(models.Manager):
    def with_related_objects(self):
        return self.select_related('author', 'location', 'category')


class PublishedPostManager(PostManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
