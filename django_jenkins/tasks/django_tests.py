# -*- coding: utf-8 -*-
# pylint: disable=W0201, W0141
"""
Build suite with normal django tests
"""
from optparse import make_option
from django.test.simple import build_suite, build_test
from django.db.models import get_app, get_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django_jenkins.tasks import BaseTask


class Task(BaseTask):
    option_list = [make_option("--tests-exclude", action="append",
                               default=[], dest="tests_excludes",
                               help="App name to exclude")]
    def __init__(self, test_labels, options):
        super(Task, self).__init__(test_labels, options)
        self.exclude_apps = []
        for appname in options['tests_excludes']:
            self.exclude_apps.append(appname)
        if not self.test_labels:
            if hasattr(settings, 'PROJECT_APPS') and not options['test_all']:
                self.test_labels = [app_name.split('.')[-1] for app_name in settings.PROJECT_APPS]

    def _check_not_excluded(self, app_name):
        if '.' in app_name:
            arr = app_name.split('.')
            for i in xrange(1, len(arr)+1):
                if '.'.join(arr[0:i]) in self.exclude_apps:
                    return False
            return True
        return app_name not in self.exclude_apps

    def build_suite(self, suite, **kwargs):
        if self.test_labels:
            for label in self.test_labels:
                if label not in self.exclude_apps:
                    if '.' in label:
                        if self._check_not_excluded(label):
                            suite.addTest(build_test(label))
                    else:
                        try:
                            app = get_app(label)
                            if self._check_not_excluded(app.__name__):
                                suite.addTest(build_suite(app))
                        except ImproperlyConfigured:
                            pass
        else:
            for app in get_apps():
                if self._check_not_excluded(app.__name__):
                    suite.addTest(build_suite(app))
