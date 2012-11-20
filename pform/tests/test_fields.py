import decimal
from webob.multidict import MultiDict
from pyramid.compat import text_type

import pform
from pform import iso8601

from base import BaseTestCase


def invalid_exc(func, *arg, **kw):
    from pform import Invalid
    try:
        func(*arg, **kw)
    except Invalid as e:
        return e
    else:
        raise AssertionError('Invalid not raised')


def strip(str):
    return ' '.join(s.strip() for s in str.split())


class TestInputField(BaseTestCase):

    def _makeOne(self, name, **kw):
        from pform.fields import InputField
        return InputField(name, **kw)

    def test_fields_text(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {})
        field.update()

        self.assertEqual(field.klass, None)

        field.readonly = True
        field.update()

        self.assertEqual(field.klass, 'disabled')


class TestTextField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.TextField(name, **kw)

    def test_fields_text(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {})
        field.update()

        self.assertEqual(field.to_form('value'), 'value')
        self.assertEqual(field.to_field('value'), 'value')

        res = ' '.join(sorted(strip(field.render()).split()))
        self.assertEqual(
            '/> <input class="text-widget" id="test" name="test" title="Test" type="text" value="content"', res)

        field.mode = pform.FORM_DISPLAY

        res = ' '.join(sorted(strip(field.render()).split()))
        self.assertIn('<span class="uneditable-input"', res)

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {'test': 'form'})
        field.update()

        res = ' '.join(sorted(strip(field.render()).split()))
        self.assertIn('input class="text-widget" id="test"', res)

        field.mode = pform.FORM_DISPLAY
        res = ' '.join(sorted(strip(field.render()).split()))
        self.assertIn('<span class="uneditable-input"', res)


class TestIntegerField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.IntegerField(name, **kw)

    def test_fields_int(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 10, {})
        field.update()

        self.assertIs(field.to_form(pform.null), pform.null)
        self.assertEqual(field.to_form(10), '10')
        self.assertRaises(pform.Invalid, field.to_form, 'value')

        self.assertIs(field.to_field(''), pform.null)
        self.assertEqual(field.to_field('10'), 10)
        self.assertRaises(pform.Invalid, field.to_field, 'value')

        res = ' '.join(sorted(strip(field.render()).split()))

        self.assertEqual(
            '/> <input class="int-widget" id="test" name="test" title="Test" type="text" value="10"', res)


class TestFloatField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.FloatField(name, **kw)

    def test_fields_float(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 10.34, {})
        field.update()

        self.assertIs(field.to_form(pform.null), pform.null)
        self.assertEqual(field.to_form(10.34), '10.34')
        self.assertRaises(pform.Invalid, field.to_form, 'value')

        self.assertIs(field.to_field(''), pform.null)
        self.assertEqual(field.to_field('10.34'), 10.34)
        self.assertRaises(pform.Invalid, field.to_field, 'value')

        res = ' '.join(sorted(strip(field.render()).split()))
        self.assertEqual(
            '/> <input class="float-widget" id="test" name="test" title="Test" type="text" value="10.34"', res)


class TestDeciamlField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.DecimalField(name, **kw)

    def test_fields_decimal(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', decimal.Decimal('10.34'), {})
        field.update()

        self.assertIs(field.to_form(pform.null), pform.null)
        self.assertEqual(field.to_form(decimal.Decimal('10.34')), '10.34')
        self.assertRaises(pform.Invalid, field.to_form, 'value')

        self.assertIs(field.to_field(''), pform.null)
        self.assertEqual(field.to_field('10.34'), decimal.Decimal('10.34'))
        self.assertRaises(pform.Invalid, field.to_field, 'value')

        res = ' '.join(sorted(strip(field.render()).split()))

        self.assertEqual(
            '/> <input class="decimal-widget" id="test" name="test" title="Test" type="text" value="10.34"',
            res)


class TestLinesField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.LinesField(name, **kw)

    def test_fields_decimal(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', ['1','2','3'], {})
        field.update()

        self.assertIs(field.to_form(pform.null), pform.null)
        self.assertEqual(field.to_form(['1','2','3']), '1\n2\n3')
        self.assertRaises(pform.Invalid, field.to_form, 1)

        self.assertIs(field.to_field(''), pform.null)
        self.assertEqual(field.to_field('1\n2\n3'), ['1','2','3'])
        self.assertRaises(pform.Invalid, field.to_field, 5)

        res = ' '.join(sorted(strip(field.render()).split()))
        self.assertIn('<textarea class="textlines-widget"', res)


class TestVocabularyField(BaseTestCase):

    def test_ctor(self):
        from pform.fields import VocabularyField

        voc = object()

        self.assertRaises(ValueError, VocabularyField, 'test')
        self.assertRaises(ValueError, VocabularyField, 'test',
                          vocabulary=voc, voc_factory=voc)

    def test_voc_factory(self):
        from pform.fields import VocabularyField

        voc = object()
        def factory(context):
            return voc

        field = VocabularyField('test', voc_factory=factory)
        clone = field.bind(self.request, 'p.', None, None)
        self.assertIs(clone.vocabulary, voc)

    def test_voc_factory_context(self):
        from pform.fields import VocabularyField

        voc = object()
        data = []
        def factory(context):
            data.append(context)
            return voc

        field = VocabularyField('test', voc_factory=factory)
        field.bind(self.request, 'p.', None, None)
        self.assertIsNone(data[-1])

        context = object()
        field.bind(self.request, 'p.', None, None, context)
        self.assertIs(data[-1], context)

    def test_vocabulary_field(self):
        voc = pform.SimpleVocabulary.from_items(
            (1, 'one', 'One'),
            (2, 'two', 'Two'),
            (3, 'three', 'Three'))

        self.assertRaises(ValueError, pform.VocabularyField, 'test')
        self.assertRaises(
            NotImplementedError,
            pform.VocabularyField('test', vocabulary=voc).is_checked,
            voc.get_term(1))

        class MyVocabularyField(pform.VocabularyField):
            def is_checked(self, term):
                return term.token == self.form_value

        field = MyVocabularyField('test', vocabulary=voc)
        field.form_value = 'one'

        self.assertTrue(field.is_checked(voc.get_term(1)))
        self.assertFalse(field.is_checked(voc.get_term(2)))

        field.id = 'test'
        field.form_value = pform.null
        field.update_items()

        self.assertEqual(field.items,
                         [{'checked': False,
                           'description': None,
                           'id': 'test-0',
                           'label': 'One',
                           'name': 'test',
                           'value': 'one'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-1',
                           'label': 'Two',
                           'name': 'test',
                           'value': 'two'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-2',
                           'label': 'Three',
                           'name': 'test',
                           'value': 'three'}])

        field.form_value = 'one'
        field.update_items()
        self.assertEqual(field.items,
                         [{'checked': True,
                           'description': None,
                           'id': 'test-0',
                           'label': 'One',
                           'name': 'test',
                           'value': 'one'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-1',
                           'label': 'Two',
                           'name': 'test',
                           'value': 'two'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-2',
                           'label': 'Three',
                           'name': 'test',
                           'value': 'three'}])


class TestBaseChoiceField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.BaseChoiceField(name, **kw)

    def test_basechoice(self):
        request = self.make_request()

        voc = pform.SimpleVocabulary.from_items(
            (1, 'one', 'One'),
            (2, 'two', 'Two'),
            (3, 'three', 'Three'))

        field = self._makeOne('test', vocabulary=voc)
        field = field.bind(request, '', 1, {})
        field.update()

        self.assertIs(field.extract(), pform.null)

        field.params = {'test': '--NOVALUE--'}
        self.assertIs(field.extract(), pform.null)

        field.params = {'test': 'three'}
        self.assertIs(field.extract(), 'three')

        self.assertIs(field.to_form(pform.null), pform.null)
        self.assertEqual(field.to_form(1), 'one')
        self.assertRaises(pform.Invalid, field.to_form, 10)
        self.assertRaises(pform.Invalid, field.to_form, [1, 10])

        self.assertIs(field.to_field(''), pform.null)
        self.assertEqual(field.to_field('one'), 1)
        self.assertRaises(pform.Invalid, field.to_field, 5)
        self.assertRaises(pform.Invalid, field.to_field, ['one','five'])


class TestBaseMultiChoiceField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.BaseMultiChoiceField(name, **kw)

    def test_basemultichoice(self):
        request = self.make_request()

        self.assertRaises(ValueError, self._makeOne, 'test')

        voc = pform.SimpleVocabulary.from_items(
            (1, 'one', 'One'),
            (2, 'two', 'Two'),
            (3, 'three', 'Three'))

        orig_field = self._makeOne('test', vocabulary=voc)
        field = orig_field.bind(request, '', [1,3], {})
        field.update()

        self.assertIs(field.to_form(pform.null), pform.null)
        self.assertEqual(field.to_form([1,2]), ['one','two'])
        self.assertRaises(pform.Invalid, field.to_form, 1)
        self.assertRaises(pform.Invalid, field.to_form, [1, 10])

        self.assertIs(field.to_field(''), pform.null)
        self.assertEqual(field.to_field(['one','three']), [1,3])
        self.assertRaises(pform.Invalid, field.to_field, 5)
        self.assertRaises(pform.Invalid, field.to_field, ['one','five'])

        field = orig_field.bind(request, '', pform.null, {})
        field.update()
        self.assertEqual(field.form_value, [])

        field = orig_field.bind(request, '', [1], {})
        field.update()
        self.assertEqual(field.form_value, ['one'])

        self.assertIs(field.extract(), pform.null)

        field.params = MultiDict((('test', field.noValueToken),
                                  ('test', 'one')))
        self.assertEqual(field.extract(), ['one'])


class TestChoiceField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.ChoiceField(name, **kw)

    def test_vocabulary_field(self):
        request = self.make_request()

        voc = pform.SimpleVocabulary.from_items(
            (1, 'one', 'One'),
            (2, 'two', 'Two'))

        field = self._makeOne('test', vocabulary=voc)
        field = field.bind(request, '', 1, {})
        field.id = 'test'
        field.update()

        self.assertEqual(field.items,
                         [{'checked': True,
                           'description': None,
                           'id': 'test-0',
                           'label': 'One',
                           'name': 'test',
                           'value': 'one'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-1',
                           'label': 'Two',
                           'name': 'test',
                           'value': 'two'}])

        field = self._makeOne('test', missing=2, vocabulary=voc)
        field = field.bind(request, '', 1, {})
        field.id = 'test'
        field.update()

        self.assertEqual(field.items,
                         [{'checked': False,
                           'description': '',
                           'id': 'test-novalue',
                           'label': 'select a value ...',
                           'name': 'test',
                           'value': '--NOVALUE--'},
                          {'checked': True,
                           'description': None,
                           'id': 'test-0',
                           'label': 'One',
                           'name': 'test',
                           'value': 'one'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-1',
                           'label': 'Two',
                           'name': 'test',
                           'value': 'two'}])


class TestMultiChoiceField(BaseTestCase):

    def _makeOne(self, name, **kw):
        return pform.MultiChoiceField(name, **kw)

    def test_fields_decimal(self):
        request = self.make_request()

        voc = pform.SimpleVocabulary.from_items(
            (1, 'one', 'One'),
            (2, 'two', 'Two'),
            (3, 'three', 'Three'))

        field = self._makeOne('test', vocabulary=voc)
        field = field.bind(request, '', [1,3], {})
        field.update()


class TestDateTime(BaseTestCase):
    def _makeOne(self, name='test', *arg, **kw):
        return pform.DateTimeField(name, request=self.request, *arg, **kw)

    def _dt(self):
        import datetime
        return datetime.datetime(2010, 4, 26, 10, 48)

    def _today(self):
        import datetime
        return datetime.date.today()

    def test_ctor_default_tzinfo_None(self):
        typ = self._makeOne()
        self.assertEqual(typ.default_tzinfo.__class__, iso8601.Utc)

    def test_ctor_default_tzinfo_non_None(self):
        tzinfo = iso8601.FixedOffset(1, 0, 'myname')
        typ = self._makeOne(default_tzinfo=tzinfo)
        self.assertEqual(typ.default_tzinfo, tzinfo)

    def test_to_form_null(self):
        typ = self._makeOne()
        result = typ.to_form(pform.null)
        self.assertEqual(result, pform.null)

    def test_to_form_with_garbage(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_form, 'garbage')
        self.assertEqual(str(e), '"garbage" is not a datetime object')

    def test_to_form_with_date(self):
        import datetime
        typ = self._makeOne()
        date = self._today()
        result = typ.to_form(date)
        expected = datetime.datetime.combine(date, datetime.time())
        expected = expected.replace(tzinfo=typ.default_tzinfo).isoformat()
        self.assertEqual(result, expected)

    def test_to_form_with_naive_datetime(self):
        typ = self._makeOne()
        dt = self._dt()
        result = typ.to_form(dt)
        expected = dt.replace(tzinfo=typ.default_tzinfo).isoformat()
        self.assertEqual(result, expected)

    def test_to_form_with_none_tzinfo_naive_datetime(self):
        typ = self._makeOne(default_tzinfo=None)
        dt = self._dt()
        result = typ.to_form(dt)
        self.assertEqual(result, dt.isoformat())

    def test_to_form_with_tzware_datetime(self):
        typ = self._makeOne()
        dt = self._dt()
        tzinfo = iso8601.FixedOffset(1, 0, 'myname')
        dt = dt.replace(tzinfo=tzinfo)
        result = typ.to_form(dt)
        expected = dt.isoformat()
        self.assertEqual(result, expected)

    def test_to_field_date(self):
        import datetime
        date = self._today()
        typ = self._makeOne()
        formatted = date.isoformat()
        result = typ.to_field(formatted)
        expected = datetime.datetime.combine(result, datetime.time())
        tzinfo = iso8601.Utc()
        expected = expected.replace(tzinfo=tzinfo)
        self.assertEqual(result.isoformat(), expected.isoformat())

    def test_to_field_invalid_ParseError(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, 'garbage')
        self.assertTrue('Invalid' in e.msg)

    def test_to_field_null(self):
        typ = self._makeOne()
        result = typ.to_field(pform.null)
        self.assertEqual(result, pform.null)

    def test_to_field_empty(self):
        typ = self._makeOne()
        result = typ.to_field('')
        self.assertEqual(result, pform.null)

    def test_to_field_success(self):
        typ = self._makeOne()
        dt = self._dt()
        tzinfo = iso8601.FixedOffset(1, 0, 'myname')
        dt = dt.replace(tzinfo=tzinfo)
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), iso)

    def test_to_field_naive_with_default_tzinfo(self):
        tzinfo = iso8601.FixedOffset(1, 0, 'myname')
        typ = self._makeOne(default_tzinfo=tzinfo)
        dt = self._dt()
        dt_with_tz = dt.replace(tzinfo=tzinfo)
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt_with_tz.isoformat())

    def test_to_field_none_tzinfo(self):
        typ = self._makeOne(default_tzinfo=None)
        dt = self._dt()
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt.isoformat())


class TestDate(BaseTestCase):

    def _makeOne(self, name='test', *arg, **kw):
        return pform.DateField(name, request=self.request, *arg, **kw)

    def _dt(self):
        import datetime
        return datetime.datetime(2010, 4, 26, 10, 48)

    def _today(self):
        import datetime
        return datetime.date.today()

    def test_to_form_null(self):
        val = pform.null
        typ = self._makeOne()
        result = typ.to_form(val)
        self.assertEqual(result, pform.null)

    def test_to_form_with_garbage(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_form, 'garbage')
        self.assertEqual(str(e), '"garbage" is not a date object')

    def test_to_form_with_date(self):
        typ = self._makeOne()
        date = self._today()
        result = typ.to_form(date)
        expected = date.isoformat()
        self.assertEqual(result, expected)

    def test_to_form_with_datetime(self):
        typ = self._makeOne()
        dt = self._dt()
        result = typ.to_form(dt)
        expected = dt.date().isoformat()
        self.assertEqual(result, expected)

    def test_to_field_invalid_ParseError(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, 'garbage')
        self.assertTrue('Invalid' in e.msg)

    def test_to_field_invalid_weird(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, '10-10-10-10')
        self.assertTrue('Invalid' in e.msg)

    def test_to_field_null(self):
        typ = self._makeOne()
        result = typ.to_field(pform.null)
        self.assertEqual(result, pform.null)

    def test_to_field_empty(self):
        typ = self._makeOne()
        result = typ.to_field('')
        self.assertEqual(result, pform.null)

    def test_to_field_success_date(self):
        typ = self._makeOne()
        date = self._today()
        iso = date.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), iso)

    def test_to_field_success_datetime(self):
        dt = self._dt()
        typ = self._makeOne()
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt.date().isoformat())


class TestFileField(BaseTestCase):

    def _makeOne(self, name, **kw):
        from pform.fields import FileField
        return FileField(name, **kw)

    def test_fields_text(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {})
        field.update()

        self.assertIs(field.extract(), pform.null)

        class FileStorage:

            def __init__(self, fp, filename, mt, s):
                self.file = fp
                self.filename = filename
                self.type = mt
                self.length = s

        fs = FileStorage(object(), 'test.jpg', 'image/jpeg', 1024)

        field = field.bind(request, '', 'content', {'test': fs})
        field.update()

        res = field.extract()
        self.assertIs(type(res), dict)
        self.assertEqual(res['filename'], 'test.jpg')

    def test_fields_html5(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {})
        field.update()

        self.assertIs(field.extract(), pform.null)

        params = {
            'test': text_type(' '*1024),
            'test-filename': 'test.jpg',
            'test-mimetype': 'image/jpeg'}

        field = field.bind(request, '', 'content', params)
        field.update()

        res = field.extract()
        self.assertIs(type(res), dict)
        self.assertEqual(res['filename'], 'test.jpg')
