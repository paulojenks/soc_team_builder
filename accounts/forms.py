from django import forms
from django.forms import inlineformset_factory, formset_factory

from . import models
from . import choices


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = models.Profile
        fields = ['first_name', 'last_name', 'bio', 'avatar']


class ProjectForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)
    skill_needs = forms.CharField(required=False)

    class Meta:
        model = models.Project
        fields = ['title', 'description', 'timeline', 'requirements', 'skill_needs']


class SkillsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.Select(choices=choices.SKILLS))

    class Meta:
        model = models.Skill
        fields = ['name']


class PositionForm(forms.ModelForm):
    skill = forms.CharField(widget=forms.Select(choices=choices.SKILLS))

    class Meta:
        model = models.Position
        fields = ['name', 'skill', 'descript']


class ApplicationForm(forms.ModelForm):
    submit = forms.BooleanField()

    class Meta:
        model = models.Application
        fields = ['submit']


class StatusForm(forms.ModelForm):
    status = forms.CharField(widget=forms.Select(choices=choices.APP_STATUS))

    class Meta:
        model = models.Application
        fields = ['status']

