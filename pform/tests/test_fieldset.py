"""
Unit tests for L{pform.fieldset}
"""
import pform
from base import BaseTestCase


field = pform.TextField(
    'test', title = 'Test node')

field1 = pform.TextField(
    'test1', title = 'Test node')


class TestFieldset(BaseTestCase):

    def test_fieldset_name_title(self):
        fieldset = pform.Fieldset(field)

        self.assertEqual(fieldset.name, '')
        self.assertEqual(fieldset.title, '')
        self.assertEqual(fieldset.prefix, '')

        fieldset = pform.Fieldset(field1, name='othername', title='Other name')

        self.assertEqual(fieldset.name, 'othername')
        self.assertEqual(fieldset.title, 'Other name')

    def test_fieldset_nested(self):
        fieldset = pform.Fieldset(
            field,
            pform.Fieldset(name='fs', *(field,)))

        self.assertEqual(fieldset['fs'].name, 'fs')
        self.assertEqual(fieldset['fs'].prefix, 'fs.')

    def test_fieldset_fields(self):
        fieldset = pform.Fieldset(field, field1)

        self.assertEqual(list(fieldset.fields()), [field, field1])

    def test_fieldset_append_simple(self):
        fieldset = pform.Fieldset(field, name='test')

        self.assertIn('test', fieldset)
        self.assertEqual(fieldset.prefix, 'test.')

        self.assertIs(fieldset['test'], field)

        self.assertRaises(ValueError, fieldset.append, field)
        self.assertRaises(TypeError, fieldset.append, object())

    def test_fieldset_append_fieldset(self):
        fieldset = pform.Fieldset(field, name='schema')
        self.assertEqual(list(fieldset.fieldsets()), [fieldset])

        fs = pform.Fieldset(field1, name='schema2', )

        fieldset.append(fs)
        self.assertEqual(len(list(fieldset.fieldsets())), 2)

        self.assertIn('schema2', fieldset)
        self.assertIs(fieldset['schema2'], fs)
        self.assertRaises(ValueError, fieldset.append, fs)

    def test_fieldset_select(self):
        fieldset = pform.Fieldset(field, field1)

        newfs = fieldset.select('test')
        self.assertNotIn('test1', newfs)
        self.assertEqual(list(newfs.keys()), ['test'])

    def test_fieldset_omit(self):
        fieldset = pform.Fieldset(field, field1)

        newfs = fieldset.omit('test')
        self.assertNotIn('test', newfs)
        self.assertEqual(list(newfs.keys()), ['test1'])

    def test_fieldset_add(self):
        fieldset = pform.Fieldset(field)
        fieldset = fieldset + pform.Fieldset(field1)

        self.assertIn('test', fieldset)
        self.assertIn('test1', fieldset)
        self.assertEqual(list(fieldset.keys()), ['test', 'test1'])

    def test_fieldset_iadd(self):
        fieldset = pform.Fieldset(field)
        fieldset += pform.Fieldset(field1)

        self.assertIn('test', fieldset)
        self.assertIn('test1', fieldset)
        self.assertEqual(list(fieldset.keys()), ['test', 'test1'])

    def test_fieldset_add_err(self):
        fieldset = pform.Fieldset(field)

        self.assertRaises(ValueError, fieldset.__add__, object())

    def test_fieldset_bind(self):
        fieldset = pform.Fieldset(field)

        request = object()
        params = object()
        data = {'test': 'CONTENT'}

        fs = fieldset.bind(request, data, params)

        self.assertIsNot(fieldset, fs)
        self.assertEqual(len(fieldset), len(fs))
        self.assertIs(fs.request, request)
        self.assertIs(fs.params, params)
        self.assertIs(fs.data, data)

        self.assertIs(fs['test'].params, params)
        self.assertEqual(fs['test'].value, 'CONTENT')

        fs = fieldset.bind(request)
        self.assertIsNot(fieldset, fs)
        self.assertEqual(len(fieldset), len(fs))
        self.assertEqual(fs.params, {})
        self.assertEqual(fs.data, {})
        self.assertEqual(fs['test'].params, {})
        self.assertIs(fs['test'].value, pform.null)

    def test_fieldset_bind_nested(self):
        fieldset = pform.Fieldset(
            field,
            pform.Fieldset(name='fs', *(field,)))

        request = object()
        params = object()
        content = {'test': 'CONTENT',
                   'fs': {'test': 'NESTED CONTENT'}}

        fs = fieldset.bind(request, content, params)

        self.assertIs(fs['fs'].request, request)
        self.assertEqual(fs['fs']['test'].value, 'NESTED CONTENT')

        fs = fieldset.bind(request)
        self.assertIs(fs['fs']['test'].value, pform.null)

    def test_fieldset_filter_in_ctor(self):
        def filter(fs, fields):
            for field in fields:
                if field.name == 'test':
                    yield field

        fieldset = pform.Fieldset(
            field, field1, filter=filter)

        fs = fieldset.bind(self.request, {}, {})
        self.assertEqual(tuple(fs.keys()), ('test',))

    def test_fieldset_filter_in_bind(self):
        def filter(fs, fields):
            for field in fields:
                if field.name == 'test':
                    yield field

        def filter1(fs, fields):
            for field in fields:
                if field.name == 'test1':
                    yield field

        fieldset = pform.Fieldset(
            field, field1, filter=filter)

        fs = fieldset.bind(self.request, {}, {}, filter=filter1)
        self.assertEqual(tuple(fs.keys()), ('test1',))

    def test_fieldset_validate(self):
        def validator(fs, data):
            raise pform.Invalid('msg', fs)

        fieldset = pform.Fieldset(field, validator=validator)
        self.assertRaises(pform.Invalid, fieldset.validate, {})

        fieldset.bind(object())
        self.assertRaises(pform.Invalid, fieldset.validate, {})

    def _makeOne(self, name, **kw):
        class MyField(pform.Field):
            def to_form(self, value):
                return value
            def to_field(self, value):
                return value

        return MyField(name, **kw)

    def test_fieldset_extract_display(self):
        field = self._makeOne('test', mode=pform.FORM_DISPLAY)
        fieldset = pform.Fieldset(field).bind(object(), None, {'test': 'VALUE'})
        data, errors = fieldset.extract()
        self.assertEqual(data, {})
        self.assertEqual(errors, [])

    def test_fieldset_extract_missing(self):
        field = self._makeOne('test')
        fieldset = pform.Fieldset(field).bind(object())

        data, errors = fieldset.extract()
        self.assertIs(errors[0].field, fieldset['test'])
        self.assertEqual(errors[0].msg, 'Required')

    def test_fieldset_extract_missing_nested(self):
        field = self._makeOne('test')
        fieldset = pform.Fieldset(
            field,
            pform.Fieldset(name='fs', *(field,))).bind(object())

        data, errors = fieldset.extract()
        self.assertIs(errors[0].field, fieldset['fs']['test'])
        self.assertIs(errors[1].field, fieldset['test'])
        self.assertEqual(errors[0].msg, 'Required')
        self.assertEqual(errors[1].msg, 'Required')

    def test_fieldset_extract(self):
        field = self._makeOne('test')
        fieldset = pform.Fieldset(field).bind(object(), params={'test': 'FORM'})

        data, errors = fieldset.extract()
        self.assertFalse(bool(errors))
        self.assertEqual(data['test'], 'FORM')

    def test_fieldset_extract_nested(self):
        field = self._makeOne('test')
        fieldset = pform.Fieldset(
            field,
            pform.Fieldset(name='fs', *(field,))
            ).bind(object, params={'test': 'FORM', 'fs.test': 'NESTED FORM'})

        data, errors = fieldset.extract()
        self.assertFalse(bool(errors))
        self.assertEqual(data['test'], 'FORM')
        self.assertEqual(data['fs']['test'], 'NESTED FORM')

    def test_fieldset_extract_preparer(self):
        def lower(val):
            return val.lower()

        field = self._makeOne('test', preparer=lower)
        fieldset = pform.Fieldset(field).bind(object, params={'test': 'FORM'})

        data, errors = fieldset.extract()
        self.assertEqual(data['test'], 'form')

    def test_fieldset_extract_validate(self):
        def validator(fs, data):
            raise pform.Invalid('msg', fs)

        field = self._makeOne('test')
        fieldset = pform.Fieldset(field, validator=validator)
        fieldset = fieldset.bind(self.request, params={'test': 'FORM'})

        data, errors = fieldset.extract()
        self.assertEqual(len(errors), 1)


class TestFieldsetErrors(BaseTestCase):

    def test_fieldset_errors(self):
        err1 = pform.Invalid('error1', field.bind(self.request,'','',{}))
        err2 = pform.Invalid('error2', field1.bind(self.request,'','',{}))

        fieldset = object()

        errors = pform.FieldsetErrors(fieldset, err1, err2)
        self.assertIn(err1, errors)
        self.assertIn(err2, errors)
        self.assertIs(errors.fieldset, fieldset)
        self.assertEqual(errors.msg, {'test': 'error1', 'test1': 'error2'})

        self.assertEqual(str(err1), "error1")
        self.assertEqual(repr(err1), "Invalid(<TextField 'test'>: <error1>)")
        self.assertEqual(str(pform.null), '<widget.null>')

        self.assertFalse(bool(pform.required))
        self.assertEqual(repr(pform.required), '<widget.required>')
