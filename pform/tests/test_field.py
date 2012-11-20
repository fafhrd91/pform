import pform
from base import BaseTestCase


field = pform.TextField(
    'test', title = 'Test node')

field1 = pform.TextField(
    'test1', title = 'Test node')


class TestField(BaseTestCase):

    def test_field_ctor(self):
        field = pform.Field('test', **{'title': 'Title',
                                      'description': 'Description',
                                      'readonly': True,
                                      'default': 'Default',
                                      'missing': 'Missing',
                                      'preparer': 'Preparer',
                                      'validator': 'validator',
                                      'custom_attr': 'Custom attr'})

        self.assertEqual(field.name, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.readonly, True)
        self.assertEqual(field.default, 'Default')
        self.assertEqual(field.missing, 'Missing')
        self.assertEqual(field.preparer, 'Preparer')
        self.assertEqual(field.validator, 'validator')
        self.assertEqual(field.custom_attr, 'Custom attr')

        self.assertEqual(repr(field), "<Field 'test'>")

    def test_field_bind(self):
        orig_field = pform.Field(
            'test', **{'title': 'Title',
                       'description': 'Description',
                       'readonly': True,
                       'default': 'Default',
                       'missing': 'Missing',
                       'preparer': 'Preparer',
                       'validator': 'validator',
                       'custom_attr': 'Custom attr'})

        field = orig_field.bind(self.request, 'field.', pform.null, {})

        self.assertEqual(field.request, self.request)
        self.assertEqual(field.value, pform.null)
        self.assertEqual(field.params, {})
        self.assertEqual(field.name, 'field.test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.readonly, True)
        self.assertEqual(field.default, 'Default')
        self.assertEqual(field.missing, 'Missing')
        self.assertEqual(field.preparer, 'Preparer')
        self.assertEqual(field.validator, 'validator')
        self.assertEqual(field.custom_attr, 'Custom attr')
        self.assertIsNone(field.context)
        self.assertIsNone(orig_field.context)

        self.assertEqual(repr(field), "<Field 'field.test'>")

        context = object()
        field = orig_field.bind(object(), 'field.', pform.null, {}, context)
        self.assertIs(field.context, context)

    def test_field_validate(self):
        field = pform.Field('test')

        self.assertIsNone(field.validate(''))
        self.assertRaises(pform.Invalid, field.validate, pform.required)

        def validator(field, value):
            raise pform.Invalid('msg', field)

        field = pform.Field('test', validator=validator)
        self.assertRaises(pform.Invalid, field.validate, '')

    def test_field_validate_type(self):
        field = pform.Field('test')
        field.typ = int

        self.assertRaises(pform.Invalid, field.validate, '')

    def test_field_extract(self):
        field = pform.Field('test')

        widget = field.bind(object(), 'field.', pform.null, {})

        self.assertIs(widget.extract(), pform.null)
        self.assertIs(widget.extract(default='test'), 'test')

        widget = field.bind(object, 'field.', pform.null, {'field.test': 'TEST'})
        self.assertIs(widget.extract(), 'TEST')
        self.assertIs(widget.extract(default='test'), 'TEST')

    def test_field_update_mode(self):
        request = object()
        field = pform.Field('test')
        widget = field.bind(request, 'field.', pform.null, {})

        widget.update()
        self.assertEqual(widget.mode, pform.FORM_INPUT)

        field = pform.Field('test', readonly=True)
        widget = field.bind(request, 'field.', pform.null, {})

        widget.update()
        self.assertEqual(widget.mode, pform.FORM_DISPLAY)

        field = pform.Field('test', mode=pform.FORM_DISPLAY)
        widget = field.bind(request, 'field.', pform.null, {})

        widget.update()
        self.assertEqual(widget.mode, pform.FORM_DISPLAY)

    def test_field_update_value(self):
        class MyField(pform.Field):
            def to_form(self, value):
                return value
            def to_field(self, value):
                return value

        request = object()

        field = MyField('test')
        widget = field.bind(request, 'field.', pform.null, {})
        widget.update()
        self.assertIs(widget.form_value, None)

        field = MyField('test', default='default value')
        widget = field.bind(request, 'field.', pform.null, {})
        widget.update()
        self.assertIs(widget.form_value, 'default value')

        field = MyField('test', default='default value')
        widget = field.bind(request, 'field.', 'content value', {})
        widget.update()
        self.assertIs(widget.form_value, 'content value')

        widget = field.bind(
            request, 'field.', pform.null, {'field.test': 'form value'})
        widget.update()
        self.assertEqual(widget.form_value, 'form value')

    def test_field_update_with_error(self):
        class MyField(pform.Field):
            def to_form(self, value):
                raise pform.Invalid('Invalid value', self)

        request = object()

        field = MyField('test')
        widget = field.bind(request, 'field.', '12345', {})
        widget.update()
        self.assertIs(widget.form_value, None)

    def test_field_get_error(self):
        err = pform.Invalid('error')

        field = pform.Field('test')
        field.error = err

        self.assertIs(field.get_error(), err)
        self.assertIsNone(field.get_error('test'))

    def test_field_get_error_suberror(self):
        err = pform.Invalid('error')
        err1 = pform.Invalid('error2', name='test')
        err['test'] = err1

        field = pform.Field('test')
        field.error = err

        self.assertIs(field.get_error('test'), err1)


class TestFieldFactory(BaseTestCase):

    def test_field_factory(self):
        class MyField(pform.Field):
            pass

        self.config.add_form_field('my-field', MyField)

        field = pform.FieldFactory(
            'my-field', 'test', title='Test field')

        self.assertEqual(field.__field__, 'my-field')

        content = object()
        params = object()

        widget = field.bind(self.request, 'field.', content, params)

        self.assertIsInstance(widget, MyField)
        self.assertIs(widget.request, self.request)
        self.assertIs(widget.value, content)
        self.assertIs(widget.params, params)
        self.assertEqual(widget.name, 'field.test')

    def test_field_no_factory(self):
        field = pform.FieldFactory(
            'new-field', 'test', title='Test field')

        self.assertRaises(
            TypeError, field.bind, self.request, '', object(), object())
