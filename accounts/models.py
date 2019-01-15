from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import EmailValidator, MinLengthValidator


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(validators=[EmailValidator])
    bio = models.TextField(blank=True, validators=[MinLengthValidator(10)])
    avatar = models.ImageField(upload_to="avatars", default="avatars/default_avatar.png")


def create_profile(sender,**kwargs ):
    if kwargs['created']:
        user_profile=Profile.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    url = models.URLField(null=True)
    description = models.CharField(max_length=200, null=True)
    timeline = models.CharField(max_length=200, null=True)
    requirements = models.TextField(null=True)
    skill_needs = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.title


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Position(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    descript = models.CharField(max_length=500, null=True)
    skill = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=100, default="open")

    def __str__(self):
        return self.name


class Application(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="undecided")

    class Meta:
        unique_together = ['user', 'position']

    def __str__(self):
        return self.position.name

