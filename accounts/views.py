from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.views.generic import TemplateView, ListView, DeleteView
from django.views.generic.edit import UpdateView, CreateView
from django.core.mail import send_mail


from django.forms import inlineformset_factory

from . import models
from . import forms
from . import choices


class SignInView(LoginView):
    """Sign in"""
    template_name = 'accounts/signin.html'


class ChangePassword(PasswordChangeView):
    pass


class RegisterView(CreateView):
    """Register as a user"""
    template_name = 'accounts/signup.html'
    form_class = UserCreationForm
    model = models.User
    success_url = reverse_lazy('accounts:sign_in')


class IndexView(TemplateView):
    """Index overview of projects"""
    template_name = 'accounts/index.html'
    model = models.Project

    def get_context_data(self, **kwargs):
        skills = []
        for skill in choices.SKILLS:
            skills.append(skill[0])
        context = super().get_context_data(**kwargs)
        context['projects'] = models.Project.objects.all()
        context['positions'] = models.Position.objects.all()
        context['skills'] = skills
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Login Required-Redirects to sign in page
    Signed in user's profile view
    """
    permission_denied_message = "Sorry, you must be signed in to view this page"
    template_name = 'accounts/profile.html'
    model = models.Profile

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context['profile'] = models.Profile.objects.get(user=user)
        context['projects'] = models.Project.objects.filter(user=user)
        context['skills'] = models.Skill.objects.filter(user=user)
        return context


@login_required(redirect_field_name='accounts:sign_in')
def delete_skill(request, pk=None):
    """Delete skill from skills list"""
    skill_to_delete = models.Skill.objects.get(id=pk)
    skill_to_delete.delete()
    return HttpResponseRedirect(reverse('accounts:profile'))


@login_required(redirect_field_name='accounts:sign_in')
def delete_position(request, pk=None):
    """Delete position from project positions"""
    position_to_delete = models.Position.objects.get(id=pk)
    position_to_delete.delete()
    return HttpResponseRedirect(reverse('accounts:profile'))


@login_required(redirect_field_name='accounts:sign_in')
def delete_application(request, pk=None):
    """Delete application from user's applications"""
    app_to_delete = models.Application.objects.get(id=pk)
    app_to_delete.delete()
    return HttpResponseRedirect(reverse('accounts:applications'))


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update profile along with adding skills and projects"""
    template_name = 'accounts/profile_edit.html'
    model = models.Profile
    second_model = models.Project
    third_model = models.Skill
    form_class = forms.inlineformset_factory(models.User, models.Profile, form=forms.ProfileForm, extra=1)
    second_form_class = inlineformset_factory(models.User, models.Project, form=forms.ProjectForm, extra=1)
    third_form_class = inlineformset_factory(models.User, models.Skill, form=forms.SkillsForm, extra=3)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)
        context['profile_formset'] = self.get_form()
        context['project_formset'] = self.second_form_class()
        context['skill_formset'] = self.third_form_class()
        context['skills'] = models.Skill.objects.filter(user=self.request.user)
        return context

    def get_success_url(self):
        return reverse('accounts:profile')

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        profile_formset = self.form_class(request.POST, request.FILES, instance=user)
        project_formset = self.second_form_class(request.POST, instance=user)
        skill_formset = self.third_form_class(request.POST, instance=user)

        if project_formset.is_valid() and profile_formset.is_valid() and skill_formset.is_valid():
            profile_formset.save()
            project_formset.save()
            skill_formset.save(commit=False)
            skills = []

            for skill in skill_formset:
                name = skill.cleaned_data.get('name')
                user = user
                if name:
                    skills.append(models.Skill(
                        name=name,
                        user=user
                    ))
            try:
                with transaction.atomic():
                    models.Skill.objects.bulk_create(skills)
            except IntegrityError:
                return HttpResponseRedirect(reverse('accounts:profile'))
            return HttpResponseRedirect(reverse('accounts:profile'))

        else:
            return self.render_to_response(self.get_context_data(
                profile_formset=profile_formset,
                project_formset=project_formset,
                skill_formset=skill_formset))


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create project with positions"""
    template_name = 'accounts/new_project.html'
    form_class = inlineformset_factory(models.User, models.Project, form=forms.ProjectForm, extra=1)
    second_form_class = inlineformset_factory(models.Project, models.Position, form=forms.PositionForm, extra=1)
    model = models.Project
    success_url = reverse_lazy('accounts:Profile')

    def get_context_data(self, **kwargs):
        context = super(ProjectCreateView, self).get_context_data(**kwargs)
        context['project_formset'] = self.form_class(prefix='project')
        context['position_form'] = self.second_form_class(prefix='position')
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        project_formset = self.form_class(request.POST, instance=user, prefix='project')
        position_form = self.second_form_class(request.POST, prefix='position')

        if project_formset.is_valid() and position_form.is_valid():
            project_formset.save()

            for position in position_form:
                if position.cleaned_data.get('name'):
                    models.Position.objects.create(
                        project = models.Project.objects.get(id=self.kwargs['pk']),
                        name = position.cleaned_data.get('name'),
                        descript = position.cleaned_data.get('descript'),
                        skill=position.cleaned_data.get('skill'),
                        status='open'
                    )

            return HttpResponseRedirect(reverse('accounts:profile'))
        else:
            project_formset = self.form_class(prefix='project')
            position_form = self.second_form_class(prefix='position')
        return render(request, 'accounts/new_project.html', {'project_formset': project_formset,
                                                             'position_form': position_form})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """Update Project- Add positions"""
    template_name = 'accounts/project_edit.html'
    model = models.Project
    form_class = forms.ProjectForm
    second_form_class = inlineformset_factory(models.Project, models.Position, form=forms.PositionForm, extra=1)
    success_url = reverse_lazy('accounts:profile')

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data(**kwargs)
        context['pos'] = models.Position.objects.filter(project=self.kwargs['pk'])
        context['project_form'] = self.form_class(instance=self.get_object(), prefix='project')
        context['position_form'] = self.second_form_class(prefix='position')
        return context

    def post(self, request, *args, **kwargs):
        project_form = self.form_class(request.POST, instance=self.get_object(), prefix='project')
        position_form = self.second_form_class(request.POST, prefix='position')
        if project_form.is_valid() and position_form.is_valid():
            models.Project.objects.filter(id=self.kwargs['pk']).update(
                title=project_form.cleaned_data.get('title'),
                description=project_form.cleaned_data.get('description'),
                requirements=project_form.cleaned_data.get('requirements'),
                skill_needs=project_form.cleaned_data.get('skill_needs'),
                timeline=project_form.cleaned_data.get('timeline')
            )
            for position in position_form:
                if position.cleaned_data.get('name'):
                    models.Position.objects.create(
                        project=models.Project.objects.get(id=self.kwargs['pk']),
                        name=position.cleaned_data.get('name'),
                        descript=position.cleaned_data.get('descript'),
                        skill=position.cleaned_data.get('skill'),
                        status='open'
                    )

            return HttpResponseRedirect(reverse('accounts:profile'))
        else:
            project_form = self.form_class()
            position_form = self.second_form_class()
        return render(request, 'accounts/project_edit.html', {'project_form': project_form,
                                                              'position_form': position_form})


class ProjectView(LoginRequiredMixin, TemplateView):
    """View Project"""
    template_name = 'accounts/project.html'
    model = models.Project

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        return get_object_or_404(models.Project, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object()
        context['positions'] = models.Position.objects.filter(project=self.get_object())
        context['all_positions'] = models.Position.objects.all()
        return context


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    """Delete project"""
    model = models.Project
    template_name = 'accounts/project_delete.html'

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        return get_object_or_404(models.Project, pk=pk)

    def get_queryset(self):
        project_id = self.object.id
        return models.Project.objects.filter(id=project_id)

    def get_success_url(self):
        return reverse('accounts:profile')


class ApplicationView(LoginRequiredMixin, ListView):
    """View Application"""
    template_name = 'accounts/applications.html'
    model = models.Application

    def get_context_data(self, *, object_list=None, **kwargs):
        skills = []
        for skill in choices.SKILLS:
            skills.append(skill[0])
        context = super().get_context_data(**kwargs)
        context['applications'] = models.Application.objects.filter(position__project__user=self.request.user)
        context['projects'] = models.Project.objects.all()
        context['profiles'] = models.Profile.objects.all()
        context['skills'] = skills
        return context


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    """Create application for existing project/position"""
    template_name = 'accounts/application.html'
    model = models.Application
    form_class = forms.ApplicationForm

    def get_queryset(self):
        pk = self.kwargs['pk']
        return models.Position.objects.get(id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.form_class()
        context['position'] = models.Position.objects.get(id=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form = form.save(commit=False)
        form.user = models.Profile.objects.get(user=self.request.user)
        form.status = "undecided"
        form.position = models.Position.objects.get(id=self.kwargs['pk'])
        form.save()
        return HttpResponseRedirect(reverse('accounts:profile'))

    def post(self, request, *args, **kwargs):
        application = self.form_class(request.POST)

        if application.is_valid():
            try:
                self.form_valid(application)
            except IntegrityError:
                messages.error(
                    self.request, 'Username or Password invalid. Please try again')
                return HttpResponseRedirect(reverse('accounts:applications'))
            return HttpResponseRedirect(reverse('accounts:applications'))

    def get_success_url(self):
        return reverse('accounts:profile')


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    """Project creator approve/deny applicants"""
    template_name = 'accounts/application_detail.html'
    model = models.Profile
    form_class = forms.StatusForm

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        return get_object_or_404(models.Application, pk=pk)

    def get_context_data(self, **kwargs):
        app = self.get_object()
        context = super().get_context_data(**kwargs)
        context['profile'] = models.Profile.objects.get(id=app.user.id)
        context['projects'] = models.Project.objects.filter(user=context['profile'].user)
        context['skills'] = models.Skill.objects.filter(user=context['profile'].user)
        context['application'] = self.form_class()
        return context

    def form_valid(self, form):
        profile = models.Profile.objects.get(id=self.request.user.id)
        applicant = models.Profile.objects.get(application=self.get_object())
        subject = "Your application for {}".format(models.Application.objects.get(id=self.kwargs['pk']))
        if form.cleaned_data.get('status') == 'approved':
            message = "Congratulations!  You've been approved!"
        elif form.cleaned_data.get('status') == 'denied':
            message = "Thank you for your interest, but there was someone else we liked better."
        else:
            message = "Your application is under review"
        recipient = applicant.user.username
        print(subject)
        print(message)
        print(profile.user.username)
        print(recipient)
        send_mail(subject=subject, message=message, from_email=profile.email, recipient_list=[recipient])
        return super(ApplicationUpdateView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        application = self.form_class(request.POST, instance=self.get_object())
        if application.is_valid():
            self.form_valid(application)
            application.save()
            return HttpResponseRedirect(reverse('accounts:applications'))
        else:
            return HttpResponseRedirect(reverse('accounts:applications'))

    def get_success_url(self):
        return reverse('accounts:applications')


@login_required(redirect_field_name='accounts:sign_in')
def search(request):
    """Search Bar- search projects based on title and/or description"""
    term = request.GET.get('q')
    projects = models.Project.objects.all()
    projects = projects.filter(
        Q(title__icontains=term) | Q(description__icontains=term))
    return render(request, 'accounts/index.html', {'projects': projects})


@login_required(redirect_field_name='accounts:sign_in')
def sort_by_skill(request, skillz=None):
    """Sort Projects based on position skills"""
    skills = []
    for skill in choices.SKILLS:
        skills.append(skill[0])
    projects = models.Project.objects.all()
    projects = projects.filter(position__skill__icontains=skillz)
    return render(request, 'accounts/index.html', {'projects': projects, 'skills': skills})
