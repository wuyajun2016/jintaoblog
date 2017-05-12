from __future__ import unicode_literals
from django.utils.six import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import  time,datetime

@python_2_unicode_compatible
class Category(models.Model):
 
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Tag(models.Model):
  
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Post(models.Model):
    title = models.CharField(max_length=70)
    
    body = models.TextField()
    
    excerpt = models.CharField(max_length=200, blank=True)

    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()

   
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)

    author = models.ForeignKey(User)

    view = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})
    def increase_views(self):
        self.view += 1
        self.save(update_fields=['view'])
    class Meta:
        ordering = ['-created_time']