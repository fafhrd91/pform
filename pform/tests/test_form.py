from webob.multidict import MultiDict
from pyramid.compat import text_
from pyramid.view import render_view_to_response
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from base import BaseTestCase, TestCase


class TestFormWidgets(TestCase):
    def _makeOne(self, fields, form, request):
        from pform.form import FormWidgets
        return FormWidgets(fields, form, request)

    def test_ctor(self):
        from pform import Form

        request = DummyRequest()
        form = Form(object(), request)
        fields = object()
        inst = self._makeOne(fields, form, request)
        self.assertEqual(inst.form_fields, fields)
        self.assertEqual(inst.form, form)
        self.assertEqual(inst.request, request)


class TestFormErrors(BaseTestCase):

    def test_form_errors(self):
        from pform import Invalid, TextField
        from pform.form import form_error_message
        request = self.make_request()

        err1 = Invalid(None, 'Error1')
        err2 = Invalid(None, 'Error2')
        err2.field = TextField('text')

        msg = [err1, err2]

        errs = form_error_message(msg, request)['errors']
        self.assertIn(err1, errs)
        self.assertNotIn(err2, errs)

        request.add_message([err1, err2], 'form:error')

        res = request.render_messages()
        self.assertIn('Please fix indicated errors.', res)

    def test_add_error_message(self):
        import pform

        request = self.make_request()

        form = pform.Form(object(), request)

        err = pform.Invalid(None, 'Error')
        form.add_error_message([err])

        res = request.render_messages()
        self.assertIn('Please fix indicated errors.', res)


class TestForm(BaseTestCase):

    def test_basics(self):
        from pform.form import Form

        request = DummyRequest()
        form = Form(None, request)

        request.url = '/test/form'
        self.assertEqual(form.action, request.url)

        self.assertEqual(form.name, 'form')

        form = Form(None, request)
        form.prefix = 'my.test.form.'
        self.assertEqual(form.name, 'my.test.form')
        self.assertEqual(form.id, 'my-test-form')

    def test_form_content(self):
        from pform.form import Form

        request = DummyRequest()
        form = Form(None, request)

        self.assertIsNone(form.form_content())

        form_content = {}
        form.content = form_content
        self.assertIs(form.form_content(), form_content)

    def test_form_content_from_update(self):
        from pform.form import Form

        request = DummyRequest()
        form = Form(None, request)

        form_content = {'test': 'test1'}
        form.update(**form_content)
        self.assertEqual(form.form_content(), form_content)

    def test_csrf_token(self):
        from pform import form

        class MyForm(form.Form):
            pass

        request = DummyRequest()
        form_ob = MyForm(None, request)

        token = form_ob.token
        self.assertEqual(token, request.session.get_csrf_token())
        self.assertIsNotNone(token)
        self.assertIsNone(form_ob.validate_csrf_token())

        request.POST = {}

        form_ob.csrf = True
        self.assertRaises(HTTPForbidden, form_ob.validate_csrf_token)
        self.assertRaises(HTTPForbidden, form_ob.validate, {}, [])

        request.POST = {form_ob.csrfname: token}
        self.assertIsNone(form_ob.validate_csrf_token())

    def test_form_params_post(self):
        from pform.form import Form, DisplayForm

        form = Form(None, self.request)
        disp_form = DisplayForm(None, self.request)

        self.assertEqual(form.method, 'post')

        post = {'post': 'info'}
        self.request.POST = post

        self.assertIs(form.form_params(), post)
        self.assertIs(disp_form.form_params(), DisplayForm.params)

    def test_form_params_get(self):
        from pform.form import Form

        form = Form(None, self.request)

        get = {'get': 'info'}
        self.request.GET = get
        form.method = 'get'
        self.assertIs(form.form_params(), get)

        form.method = 'unknown'
        self.assertEqual(form.form_params(), None)

    def test_form_convert_params_to_multidict(self):
        from pform.form import Form

        form = Form(None, self.request)

        params = {'params': 'info'}
        form.method = 'POST'
        form.params = params
        self.assertIn('params', form.form_params().keys())
        self.assertIsInstance(form.form_params(), MultiDict)

        params = MultiDict({'params': 'info'})
        form.method = 'POST'
        form.params = params
        self.assertIs(form.form_params(), params)

    def test_form_params_method(self):
        from pform.form import Form

        form = Form(None, None)
        form.method = 'params'
        params = {'post': 'info'}
        form.params = params

        self.assertEqual(list(form.form_params().keys()), ['post'])
        self.assertEqual(list(form.form_params().values()), ['info'])

    def test_form_mode(self):
        from pform.form import Form, DisplayForm, \
            FORM_INPUT, FORM_DISPLAY

        request = DummyRequest()

        form = Form(None, request)
        self.assertEqual(form.mode, FORM_INPUT)

        form = DisplayForm(None, request)
        self.assertEqual(form.mode, FORM_DISPLAY)

    def test_form_update_widgets(self):
        import pform

        request = DummyRequest()
        request.POST = {}

        form_ob = pform.Form(None, request)
        form_ob.update()

        self.assertIsInstance(form_ob.widgets, pform.FormWidgets)
        self.assertEqual(form_ob.widgets.mode, form_ob.mode)

        form_ob.mode = pform.FORM_DISPLAY
        form_ob.update()
        self.assertEqual(form_ob.widgets.mode, pform.FORM_DISPLAY)

        self.assertEqual(len(form_ob.widgets), 0)

        form_ob.fields = pform.Fieldset(pform.TextField('test'))
        form_ob.update()
        self.assertEqual(len(form_ob.widgets), 1)
        self.assertIn('test', form_ob.widgets)
        self.assertIn('test', [f.name for f in form_ob.widgets.fields()])

        self.assertIsInstance(form_ob.widgets['test'], pform.TextField)
        self.assertEqual(form_ob.widgets['test'].name, 'test')
        self.assertEqual(form_ob.widgets['test'].id, 'form-widgets-test')

    def test_form_extract(self):
        import pform

        request = DummyRequest()
        request.POST = {}

        form_ob = pform.Form(None, request)
        form_ob.fields = pform.Fieldset(pform.TextField('test'))
        form_ob.update()

        data, errors = form_ob.extract()
        self.assertEqual(errors[0].msg, 'Required')

        request.POST = {'test': 'Test string'}
        form_ob.update()
        data, errors = form_ob.extract()
        self.assertEqual(data['test'], 'Test string')

    def test_form_render(self):
        import pform

        request = self.make_request()

        form_ob = pform.Form(None, request)
        form_ob.fields = pform.Fieldset(pform.TextField('test'))
        form_ob.update()

        self.assertIn('<form action="http://example.com"', form_ob.render())

    def test_form_render_bytes(self):
        import pform

        class MyForm(pform.Form):
            def render(self):
                return b'binary'

        form_ob = MyForm(None, self.request)
        form_ob.fields = pform.Fieldset(pform.TextField('test'))
        res = form_ob()

        self.assertIn('binary', res.body)

    def test_form_render_view_config_renderer(self):
        import pform
        request = self.make_request()

        class CustomForm(pform.Form):
            fields = pform.Fieldset(pform.TextField('test'))

        self.config.add_view(
            name='test', view=CustomForm,
            renderer='pform:tests/test-form.pt')

        resp = render_view_to_response(None, request, 'test', False).body

        self.assertIn(b'<h1>Custom form</h1>', resp)
        self.assertIn(b'<form action="http://example.com"', resp)

    def test_form_render_view_config(self):
        import pform
        request = self.make_request()

        class CustomForm(pform.Form):
            fields = pform.Fieldset(pform.TextField('test'))

        self.config.add_view(name='test', view=CustomForm)

        resp = render_view_to_response(None, request, 'test', False).body
        self.assertIn('<form action="http://example.com"', text_(resp))

    def test_form_render_view_config_return(self):
        import pform
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(pform.Form):
            fields = pform.Fieldset(pform.TextField('test'))

            @pform.button('test')
            def handler(self):
                return HTTPFound(location='.')

        res = CustomForm(object(), request)()
        self.assertIsInstance(res, HTTPFound)


class DummyForm(object):
    context = None
    prefix = 'prefix'
    def form_params(self):
        return None
    def form_content(self):
        return None


class DummyFieldset(object):
    def fieldsets(self):
        return []


class DummyFields(object):
    def __init__(self, fieldset=None):
        if fieldset is None:
            fieldset = DummyFieldset()
        self.fieldset = fieldset

    def bind(self, data, params, context=None):
        self.data = data
        self.params = params
        self.context = context
        return self.fieldset
