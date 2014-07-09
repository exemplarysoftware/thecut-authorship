# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.test import TestCase
from django import forms
from mock import patch
from test_app.models import AuthorshipModel
from thecut.authorship.factories import UserFactory
from thecut.authorship.forms import AuthorshipMixin


class AuthorshipModelForm(AuthorshipMixin, forms.ModelForm):

    class Meta:
        model = AuthorshipModel
        fields = []


class DummyUser(object):

    pass


class TestAuthorshipMixin(TestCase):

    def test_requires_an_extra_argument_on_creating_an_instance(self):
        self.assertRaises(TypeError, AuthorshipModelForm)

    def test_sets_user_attribute(self):

        dummy_user = DummyUser()

        form = AuthorshipModelForm(user=dummy_user)

        self.assertEqual(dummy_user, form.user)


class DummyUnsavedModel(object):

    def __init__(self):
        self.pk = None


class TestAuthorshipMixinSave(TestCase):

    @patch('django.forms.ModelForm.save')
    def test_calls_super_class_save_method(self, superclass_save):

        form = AuthorshipModelForm(user=UserFactory())
        form.instance = DummyUnsavedModel()

        form.save()

        self.assertTrue(superclass_save.called)

    @patch('django.forms.ModelForm.save')
    def test_sets_updated_by_to_given_user(self, superclass_save):
        user = DummyUser()
        form = AuthorshipModelForm(user=user)
        form.instance = DummyUnsavedModel()
        form.cleaned_data = {}

        form.save()

        self.assertEqual(user, form.instance.updated_by)

    @patch('django.forms.ModelForm.save')
    def test_sets_created_by_if_instance_is_not_saved(self, superclass_save):
        user = DummyUser()
        form = AuthorshipModelForm(user=user)
        form.instance = DummyUnsavedModel()
        form.cleaned_data = {}

        form.save()

        self.assertEqual(user, form.instance.created_by)

    @patch('django.forms.ModelForm.save')
    def test_does_not_set_created_by_if_instance_is_saved(self,
                                                          superclass_save):

        class DummySavedModel(object):

            def __init__(self):
                self.pk = 'arbitrary-value'
                self.created_by = 'arbitrary-value'

        user = DummyUser()
        form = AuthorshipModelForm(user=user)
        form.instance = DummySavedModel()
        form.cleaned_data = {}

        form.save()

        self.assertNotEqual(user, form.instance.created_by)