from django.test import TestCase, Client
from django.urls import reverse
from django_webtest import WebTest

from . import models
from . import forms


class FormTest(WebTest):
    def setUp(self):
        self.new_user = models.User.objects.create(
            username="test@test.com",
        )
        self.new_user.set_password('password')
        self.new_user.save()

        self.new_project = models.Project.objects.create(
            user_id=1,
            id=1,
            title="Test Project",
            description="Test Description",
            timeline="Test Timeline",
            skill_needs="Test Skills",
            requirements="Test Requirements"
        )

        self.new_position = models.Position.objects.create(
            id=11,
            name="Test Position",
            skill="Django",
            descript="Position Description",
            project=self.new_project,
            status="open"
        )

        self.new_application = models.Application.objects.create(
            id=11,
            user= self.new_user.profile,
            position= self.new_position,
            status='undecided'
        )

    def test_login(self):
        form = self.app.get(reverse('accounts:sign_in'), user="test@test.com").forms[1]
        form['username'] = "test@test.com"
        form['password'] = "password"
        response = form.submit().follow()
        print(response.status)
        self.assertEqual(response.status_code, 200)

    def test_edit_profile(self):
        form = self.app.get(reverse('accounts:edit_profile'), user="test@test.com").forms[1]
        form['profile-0-first_name'] = "test"
        form['profile-0-last_name'] = "test"
        form['profile-0-bio'] = "This is a test biography"
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)

    def test_search_bar(self):
        form = self.app.get(reverse('accounts:index'), user="test@test.com").forms[0]
        form['q'] = "test"
        response = form.submit()
        self.assertEqual(response.status_code, 200)

    def test_sort_by_skill(self):
        response = self.app.get(reverse('accounts:sort', kwargs={'skillz': "test"}), user="test@test.com")
        self.assertEqual(response.status_code, 200)

    def test_create_project(self):
        form = self.app.get(reverse('accounts:project_new'), user="test@test.com").forms[1]
        form['project-0-title'] = "Test Project"
        form['project-0-description'] = "Test Project Description"
        form['project-0-timeline'] = "Test Days"
        form['project-0-requirements'] = "Test requirements"
        form['project-0-skill_needs'] = "Test Skill Needs"
        response = form.submit().follow()
        create_response = form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(create_response.status_code, 302)

    def test_edit_project(self):
        form = self.app.get(reverse('accounts:project_edit', kwargs={'pk': 1}), user="test@test.com").forms[1]
        form['project-title'] = "Test Project Again"
        form['project-description'] = "Test Project Description"
        form['project-timeline'] = "Test Days"
        form['project-requirements'] = "Test requirements"
        form['project-skill_needs'] = "Test Skill Needs"
        form['position-0-descript'] = "Position Description"
        form['position-0-name'] = "Position Name"
        form['position-0-skill'] = "Python"
        form['position-0-project'] = "Test Project Again"
        form['position-0-id'] = 22
        response = form.submit()
        self.assertEqual(response.status_code, 200)

    def test_create_application(self):
        form = self.app.get(reverse('accounts:application_new', kwargs={'pk': 11}), user="test@test.com").forms[1]
        form['submit'] = True
        response = form.submit()
        self.assertEqual(response.status_code, 302)

    def test_update_application(self):
        response = self.app.get(reverse('accounts:application_detail', kwargs={'pk': 11}), user="test@test.com")
        form = self.app.get(reverse('accounts:application_detail', kwargs={'pk': 11}), user="test@test.com").forms[1]
        form['status'] = 'approved'
        resp = form.submit()
        self.assertEqual(resp.status_code,302)
        self.assertEqual(response.status_code, 200)

    def test_update_application_denial(self):
        response = self.app.get(reverse('accounts:application_detail', kwargs={'pk': 11}), user="test@test.com")
        form = self.app.get(reverse('accounts:application_detail', kwargs={'pk': 11}), user="test@test.com").forms[1]
        form['status'] = 'denied'
        resp = form.submit()
        self.assertEqual(resp.status_code,302)
        self.assertEqual(response.status_code, 200)


class ViewsTest(TestCase):
    def setUp(self):
        self.new_user = models.User.objects.create(
            username="test@test.com",
        )
        self.new_user.set_password('password')
        self.new_user.save()

        self.new_project = models.Project.objects.create(
            user_id=1,
            id=1,
            title="Test Project",
            description="Test Description",
            timeline="Test Timeline",
            skill_needs="Test Skills",
            requirements="Test Requirements"
        )

        self.client = Client()

    def test_user_create(self):
        """Assert that new_user has been created and is in the db"""
        self.assertIn(self.new_user, models.User.objects.all())

    def test_project_view(self):
        user_login = self.client.login(username="test@test.com", password="password")
        response = self.client.get(reverse('accounts:project', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_profile_view(self):
        user_login = self.client.login(username="test@test.com", password="password")
        self.assertTrue(user_login)
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_applications_list(self):
        user_login = self.client.login(username="test@test.com", password="password")
        response = self.client.get(reverse('accounts:applications'))
        self.assertEqual(response.status_code, 200)


class DeleteTests(TestCase):
    def setUp(self):
        self.new_user = models.User.objects.create(
            username="test@test.com",
        )
        self.new_user.set_password('password')
        self.new_user.save()

        self.project_new = models.Project.objects.create(
            user_id=1,
            id=1,
            title="Test Project",
            description="Test Description",
            timeline="Test Timeline",
            skill_needs="Test Skills",
            requirements="Test Requirements"
        )

        self.skill_new = models.Skill.objects.create(
            user_id=1,
            id=1,
            name="Test Skill"
        )

        self.position_new = models.Position.objects.create(
            id=1,
            name="Test Position",
            skill="Django",
            descript="Position Description",
            project=self.project_new,
            status="open"
        )

        self.application_new = models.Application.objects.create(
            id=1,
            user_id=1,
            position=self.position_new,
            status='undecided'
        )

    def test_delete_project(self):
        self.client.login(username="test@test.com", password="password")
        response = self.client.get(reverse('accounts:project_delete', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 200)

    def test_delete_skill(self):
        self.client.login(username="test@test.com", password="password")
        response = self.client.get(reverse('accounts:skill_delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

    def test_delete_position(self):
        self.client.login(username="test@test.com", password="password")
        response = self.client.get(reverse('accounts:position_delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

    def test_delete_application(self):
        self.client.login(username="test@test.com", password="password")
        response = self.client.get(reverse('accounts:application_delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)
