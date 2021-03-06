# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import RequestFactory
from djangular.core.urlresolvers import get_all_remote_methods, get_current_remote_methods
from server.tests.urls import RemoteMethodsView


class TemplateRemoteMethods(TestCase):
    urls = 'server.tests.urls'

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_current_remote_methods(self):
        view = RemoteMethodsView()
        view.request = self.factory.get('/straight_methods/')
        remote_methods = get_current_remote_methods(view)
        self.assertDictEqual({'foo': {'url': u'/straight_methods/', 'headers': {'DjNg-Remote-Method': 'foo'}, 'method': 'auto'}, 'bar': {'url': u'/straight_methods/', 'headers': {'DjNg-Remote-Method': 'bar'}, 'method': 'auto'}},
                             remote_methods)

    def test_get_all_remote_methods(self):
        remote_methods = get_all_remote_methods()
        self.assertDictEqual(remote_methods, {'submethods': {'sub': {'app': {'foo': {'url': '/sub_methods/sub/app/', 'headers': {'DjNg-Remote-Method': 'foo'}, 'method': 'auto'}, 'bar': {'url': '/sub_methods/sub/app/', 'headers': {'DjNg-Remote-Method': 'bar'}, 'method': 'auto'}}}}, 'straightmethods': {'foo': {'url': '/straight_methods/', 'headers': {'DjNg-Remote-Method': 'foo'}, 'method': 'auto'}, 'bar': {'url': '/straight_methods/', 'headers': {'DjNg-Remote-Method': 'bar'}, 'method': 'auto'}}})
