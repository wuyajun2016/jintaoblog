from __future__ import unicode_literals
from django.utils.six import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

@python_2_unicode_compatible
class UserProfile(models.Model):
    nickname = models.CharField(max_length=50, blank=True)
    user = models.OneToOneField(User)
    sex = models.IntegerField(default=0)
    phone = models.CharField(max_length=16, default='', blank=True)
    def __str__(self):
        return self.nickname

    def __unicode__(self):
        return self.nickname

    def save(self,*args,**kwargs):
        if not self.pk:
            try:
                p = UserProfile.objects.get(user=self.user)
                self.pk = p.pk
            except UserProfile.DoesNotExist:
                pass
        super(UserProfile, self).save(*args,**kwargs)
    #we will now define signals so our Profile model will be automatically created/updated when we create/update User instances
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            profile = UserProfile()
            profile.user = instance
            profile.save()

    post_save.connect(create_user_profile, sender=User)
class User_forgetpassword(models.Model):
    user_fp = models.ForeignKey(User)
    valid_code = models.CharField(max_length=24)
    valid_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % (self.valid_time)

