import mock
import pform
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationConflictError

from base import BaseTestCase


class TestFieldset(BaseTestCase):

    @mock.patch('pform.directives.venusian')
    def test_declarative(self, m_venusian):

        @pform.field('my-field')
        class MyField(pform.Field):
            pass

        wrp, cb = m_venusian.attach.call_args[0]

        self.assertIs(wrp, MyField)

        m_venusian.config.with_package.return_value = self.config
        cb(m_venusian, 'my-field', MyField)

        self.assertIs(pform.get_field_factory(self.request, 'my-field'), MyField)

    def test_imperative(self):
        class MyField(pform.Field):
            """ """

        self.config.provide_form_field('my-field', MyField)
        self.assertIs(pform.get_field_factory(self.request, 'my-field'), MyField)

    def test_conflict(self):

        class MyField(pform.Field):
            pass

        class MyField2(pform.Field):
            pass

        config = Configurator()
        config.include('pform')
        config.provide_form_field('my-field', MyField)
        config.provide_form_field('my-field', MyField2)

        self.assertRaises(ConfigurationConflictError, config.commit)

    @mock.patch('pform.directives.venusian')
    def test_preview(self, m_venusian):

        class MyField(pform.Field):
            pass

        @pform.fieldpreview(MyField)
        def preview(request):
            """ """

        wrp, cb = m_venusian.attach.call_args[0]

        self.assertIs(wrp, preview)

        m_venusian.config.with_package.return_value = self.config
        cb(m_venusian, MyField, preview)

        from pform.directives import ID_PREVIEW
        previews = self.registry[ID_PREVIEW]

        self.assertIn(MyField, previews)
        self.assertIs(previews[MyField], preview)
        self.assertIs(pform.get_field_preview(self.request, MyField), preview)
