import mock
import pform
from base import TestCase, BaseTestCase


class TestCompositeError(TestCase):
    """ Tests for pform.CompositeError """

    def test_type(self):
        self.assertTrue(
            issubclass(pform.CompositeError, pform.Invalid))

    def test_repr(self):
        err = pform.CompositeError('test')
        self.assertIn('CompositeError<: test>:\n{', repr(err))


class TestCompositeField(BaseTestCase):
    """ Tests for pform.CompositeField """

    def test_ctor(self):
        """ Composite field requires fields """
        self.assertRaises(
            ValueError, pform.CompositeField, 'test')

    def test_ctor_fields(self):
        """ Composite field converts sequence of fields to Fieldset """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('firstname'),
                            pform.TextField('lastname')))
        self.assertIsInstance(field.fields, pform.Fieldset)

    def test_default(self):
        """ Default composite field value """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('firstname'),
                            pform.TextField('lastname')))
        self.assertEqual(
            {'lastname': '', 'firstname': ''}, field.default)

    def test_default_from_fields(self):
        """ Set default composite field value """
        field = pform.CompositeField(
            'test',
            fields=(pform.TextField('firstname',default='1'),
                    pform.TextField('lastname', default='2')))
        self.assertEqual(
            {'lastname': '2', 'firstname': '1'}, field.default)

    def test_set_default(self):
        """ Set default composite field value """
        field = pform.CompositeField(
            'test',
            default={'firstname': '123'},
            fields=(pform.TextField('firstname'),
                    pform.TextField('lastname')))
        self.assertEqual(
            {'firstname': '123'}, field.default)

    def test_ctor_fields_prefix(self):
        """ Composite field uses custom fields prefix """
        field = pform.CompositeField(
            'test', fields=pform.Fieldset(
                pform.TextField('firstname'),
                pform.TextField('lastname'),
                name = 'fieldset'))

        self.assertEqual('test.', field.fields.prefix)

    def test_bind(self):
        """ Composite field convert null value into dictionary """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('firstname'),))

        widget = field.bind(self.request, '', pform.null, {})
        self.assertEqual({}, widget.value)

        widget = field.bind(self.request, '', None, {})
        self.assertEqual({}, widget.value)

        self.assertEqual(pform.null, widget.fields['firstname'].value)

        self.assertEqual('test', widget.name)
        self.assertEqual('test.firstname', widget.fields['firstname'].name)

    def test_bind_fields(self):
        """ Composite field bind fields as well """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('firstname'),))

        widget = field.bind(self.request, '', {'firstname': 'Nikolay'}, {})
        self.assertEqual('Nikolay', widget.fields['firstname'].value)

    def test_bind_flat_fields(self):
        """ Composite field bind flat fields """
        field = pform.CompositeField(
            'test', fields=(
                pform.CompositeField(
                    'sub', flat=True, fields=(pform.TextField('firstname'),)),
                pform.TextField('lastname')))

        widget = field.bind(self.request, '',
                            {'firstname': 'Nikolay', 'lastname': 'Kim'}, {})
        self.assertEqual(
            'Nikolay', widget.fields['sub'].fields['firstname'].value)

    def test_set_id_prefix(self):
        """ Composite field sets id for subfields """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('firstname'),))

        field.set_id_prefix('prefix.')
        self.assertEqual('prefix-test', field.id)
        self.assertEqual('prefix-test-firstname', field.fields['firstname'].id)

    def test_extract(self):
        """ Extract form data """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('firstname'),
                            pform.TextField('lastname')))

        widget = field.bind(self.request, '', None,
                            {'test.lastname': pform.null,
                             'test.firstname':'Nikolay'})
        result = widget.extract()
        self.assertEqual({'lastname': '', 'firstname': 'Nikolay'}, result)

    def test_extract_missing(self):
        """ Extract returns missing """
        fields=(pform.TextField('firstname', missing='name'),
                pform.TextField('lastname'))

        field = pform.CompositeField('test', fields=fields)

        widget = field.bind(self.request, '', None, {})

        result = widget.extract()
        self.assertEqual({'lastname': fields[1].missing,
                          'firstname': fields[0].missing}, result)

    def test_form_extract_missing(self):
        """ Extract form data, composite field no data """
        fields=(pform.TextField('firstname', missing='name'),
                pform.TextField('lastname'))

        field = pform.CompositeField('test', fields=fields)

        form = pform.Form(object(), self.request, fields=(field,))
        form.update_form()

        data, errors = form.extract()
        self.assertEqual({'lastname': fields[1].missing,
                          'firstname': fields[0].missing}, data['test'])

    def test_validate(self):
        """ Validate data """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('firstname'),
                            pform.TextField('lastname')))

        with self.assertRaises(pform.Invalid) as cm:
            field.validate({'lastname':'', 'firstname': 'Nikolay'})

        err = cm.exception
        self.assertEqual(1, len(err.errors))
        self.assertIn('lastname', err)

    def test_validate_consolidate_errs(self):
        """ Validate data (consolidate_errors) """
        field = pform.CompositeField(
            'test',
            consolidate_errors=True,
            fields=(pform.TextField('firstname'),
                    pform.TextField('lastname')))

        with self.assertRaises(pform.Invalid) as cm:
            field.validate({'lastname':'', 'firstname': 'Nikolay'})

        err = cm.exception
        self.assertEqual(0, len(err.errors))
        self.assertIn('Required', err.msg)

    def test_custom_validator(self):
        """ Custom validator """
        v = mock.Mock()
        field = pform.CompositeField(
            'test', fields=(pform.TextField('firstname'),
                            pform.TextField('lastname')),
            validator=v
        )
        field.validate({'lastname':'Kim', 'firstname': 'Nikolay'})
        self.assertIs(v.call_args[0][0], field)

    def test_to_field_exception(self):
        """ Composite field, convert form data to field data with error """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('name'),
                            pform.IntegerField('age')))

        with self.assertRaises(pform.Invalid) as cm:
            field.to_field({'name': 'Nikolay', 'age': 'www'})

        self.assertIn('age', cm.exception)

    def test_to_field_exception_consolidate_errs(self):
        """ Composite field, convert form data to field data with error (consolidate) """
        field = pform.CompositeField(
            'test',
            consolidate_errors = True,
            fields=(pform.TextField('name'),
                    pform.IntegerField('age')))

        with self.assertRaises(pform.Invalid) as cm:
            field.to_field({'name': 'Nikolay', 'age': 'www'})

        self.assertNotIn('age', cm.exception)
        self.assertEqual('"${val}" is not a number', cm.exception.msg)

    def test_to_field(self):
        """ Composite field, convert form data to field data """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('name'),
                            pform.IntegerField('age')))

        result = field.to_field({'name': 'Nikolay', 'age': '123'})
        self.assertEqual({'name':'Nikolay', 'age':123}, result)

    def test_update(self):
        """ Composite field, update subfields """
        field = pform.CompositeField('test', fields=(pform.TextField('name'),))

        widget = field.bind(self.request, '', None,
                            {'test.name': 'Nikolay'})
        widget.update()

        self.assertEqual('Nikolay', widget.fields['name'].form_value)

    def test_flatten(self):
        """ Composite field, flatten """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('name'),
                            pform.TextField('age'),))

        self.assertEqual({'name':'n', 'age': '123'},
                         field.flatten({'name':'n', 'age': '123'}))

        self.assertEqual({'name':'n', 'age': '123', 'extra':'1'},
                         field.flatten({'name':'n', 'age': '123','extra':'1'}))

    def test_flatten_recursive(self):
        """ Composite field, recursive flatten """
        field = pform.CompositeField(
            'test', fields=(
                pform.TextField('name'),
                pform.CompositeField(
                    'address', flat=True,
                    fields=(pform.TextField('street'),))))

        self.assertEqual(
            field.flatten({'name':'n', 'address': {'street':'123'}}),
            {'name':'n', 'street': '123'})

    def test_render_widget(self):
        """ Composite field render widget """
        field = pform.CompositeField(
            'test', title='Test', fields=(pform.TextField('name'),))

        widget = field.bind(self.request, '', None,
                            {'test.name': 'Nikolay'})
        widget.update()

        res = widget.render_widget()
        self.assertIn(
            '<label class="control-label">Test', res)
        self.assertIn(
            '<input type="text" class="text-widget" value="Nikolay"', res)

    def test_render_widget_with_error(self):
        """ Composite field render widget with error """
        field = pform.CompositeField('test', fields=(pform.TextField('name'),))

        widget = field.bind(self.request, '', None, {})
        widget.update()
        self.assertRaises(pform.Invalid, widget.validate, {'name': ''})

        res = widget.render_widget()
        self.assertIn('<div class="control-group error">', res)
        self.assertIn('<span class="help-inline">Required</span>', res)

    def test_render(self):
        """ Composite field render """
        field = pform.CompositeField(
            'test', fields=(pform.TextField('name', title='Name'),))

        widget = field.bind(self.request, '', None,
                            {'test.name': 'Nikolay'})
        widget.update()

        res = widget.render()
        self.assertIn(
            '<input type="text" class="text-widget" value="Nikolay" id="test-test-name" name="test.name" title="Name">', res)
