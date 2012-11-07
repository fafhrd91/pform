"""Form implementation"""
from collections import OrderedDict
from webob.multidict import MultiDict
from pyramid.decorator import reify
from pyramid.renderers import NullRendererHelper
from pyramid.interfaces import IResponse
from pyramid.httpexceptions import HTTPForbidden
from pyramid.config.views import DefaultViewMapper
from player import render, tmpl_filter, add_message

from pform.field import Field
from pform.fieldset import Fieldset
from pform.button import Buttons, Actions
from pform.interfaces import Invalid, FORM_INPUT, FORM_DISPLAY


@tmpl_filter('form:error')
def form_error_message(context, request):
    """ form error renderer """
    errors = [err for err in context
              if isinstance(err, Invalid) and err.field is None]

    return {'errors': errors}


class FormWidgets(OrderedDict):
    """ Form widgets manager.
    Widget is bound to content field. """

    mode = FORM_INPUT
    prefix = 'widgets.'
    fieldsets = ()

    def __init__(self, fields, form, request):
        self.form_fields = fields
        self.form = form
        self.request = request

        super(FormWidgets, self).__init__()

    def fields(self):
        return self.fieldset.fields()

    def update(self):
        form = self.form
        params = form.form_params()
        content = form.form_content()
        prefix = '%s%s' % (form.prefix, self.prefix)

        self.fieldset = self.form_fields.bind(
            self.request, content, params, form.context)
        self.fieldsets = fieldsets = []

        # Walk through each field, making a widget out of it.
        for fieldset in self.fieldset.fieldsets():
            widgets = []

            for widget in fieldset.fields():
                if widget.mode is None:
                    widget.mode = self.mode
                widget.id = ('%s%s' % (prefix, widget.name)).replace('.', '-')
                widget.tmpl_widget = form.tmpl_widget
                widget.update()
                widgets.append(widget)
                self[widget.name] = widget

            fieldsets.append(
                {'fieldset': fieldset,
                 'name': fieldset.name,
                 'title': fieldset.title,
                 'widgets': widgets})

    def extract(self):
        data, errors = self.fieldset.extract()

        # additional form validation
        self.form.validate(data, errors)

        # set errors to fields
        for err in errors:
            if isinstance(err.field, Field) and err.field.error is None:
                err.field.error = err

        return data, errors


class FormViewMapper(DefaultViewMapper):

    def __init__(self, **kw):
        super(FormViewMapper, self).__init__(**kw)

        renderer = kw.get('renderer')
        if not (renderer is None or isinstance(renderer, NullRendererHelper)):
            self.map_class_native = self.map_class_native_update

    def map_class_native_update(self, form_view):
        def _class_view(context, request, _view=form_view):
            inst = _view(context, request)
            request.__original_view__ = inst
            res = inst.render_update()
            request.__view__ = inst
            return res
        return _class_view


class Form(object):
    """ A form

    ``id``: Form id

    ``name``: Form name

    ``label``: Form label

    ``description``: Form description

    ``prefix``: Form prefix, it used for html elements `id` generations.

    ``fields``: Form fields :py:class:`ptah.form.Fieldset`

    ``buttons``: Form buttons :py:class:`ptah.form.Buttons`

    ``actions``: Instance of :py:class:`ptah.form.Actions` class

    ``widgets``: Instance of :py:class:`FormWidgets` class

    ``content``: Form content, it should be `None` or dictionary with
    data for fields.

    ``params``: None

    ``mode``: Form mode. It can be :py:data:`ptah.form.FORM_INPUT` or
        :py:data:`ptah.form.FORM_DISPLAY`

    ``action``: Form action, by default ``request.url``

    ``method``: HTML Form method (`post`, `get`)

    ``csrf``: Enable/disable form csrf protection

    ``token``: csrf token

    ``csrf-name``: csrf field name
    """

    label = None

    description = ''

    prefix = 'form.'

    actions = None

    widgets = None

    buttons = None

    fields = Fieldset()

    content = None

    mode = FORM_INPUT

    method = 'post'
    enctype = 'multipart/form-data'
    accept = None
    acceptCharset = None
    params = None
    context = None
    klass = 'form-horizontal'

    csrf = False
    csrfname = 'csrf-token'

    tmpl_view = 'form:view'
    tmpl_actions = 'form:actions'
    tmpl_widget = 'fields:widget'

    __name__ = ''
    __parent__ = None

    __view_mapper__ = FormViewMapper

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

        if self.buttons is None:
            self.buttons = Buttons()

    @reify
    def action(self):
        return self.request.url

    @reify
    def name(self):
        return self.prefix.strip('.')

    @reify
    def id(self):
        return self.name.replace('.', '-')

    def form_content(self):
        """ Return form content.
        By default it returns ``Form.content`` attribute. """
        return self.content

    def form_params(self):
        """ get request params """
        if self.params is not None:
            if not isinstance(self.params, MultiDict):
                return MultiDict(self.params)
            return self.params

        if self.method == 'post':
            return self.request.POST
        elif self.method == 'get':
            return self.request.GET
        else:
            return self.params

    def add_error_message(self, msg):
        """ add form error message """
        add_message(self.request, msg, 'form:error')

    def update_widgets(self):
        """ prepare form widgets """
        self.widgets = FormWidgets(self.fields, self, self.request)
        self.widgets.mode = self.mode
        self.widgets.update()

    def update_actions(self):
        """ Prepare form actions, this method should be called directly.
        ``Form.update`` calls this method during initialization."""
        self.actions = Actions(self, self.request)
        self.actions.update()

    @property
    def token(self):
        return self.request.session.get_csrf_token()

    def validate(self, data, errors):
        """ additional form validation """
        self.validate_csrf_token()

    def validate_csrf_token(self):
        """ csrf token validation """
        if self.csrf:
            token = self.form_params().get(self.csrfname, None)
            if token is not None:
                if self.token == token:
                    return

            raise HTTPForbidden("Form authenticator is not found.")

    def extract(self):
        """ extract form values """
        return self.widgets.extract()

    def update(self, **data):
        """ update form """
        if not self.content and data:
            self.content = data

        self.update_widgets()
        self.update_actions()

        return self.actions.execute()

    def render(self):
        """ render form """
        return render(self.request, self.tmpl_view, self)

    def render_update(self):
        result = self.update()
        if result is None:
            result = {}

        return result

    def __call__(self):
        """ update form and render form to response """
        result = self.update()

        response = self.request.registry.queryAdapterOrSelf(result, IResponse)
        if response is not None:
            return response

        response = self.request.response
        body = self.render()
        if isinstance(body, bytes):
            response.body = body
        else:
            response.text = body
        return response


class DisplayForm(Form):
    """ Special form that just display content """

    mode = FORM_DISPLAY
    params = MultiDict([])

    tmpl_view = 'form:form-display'
    tmpl_widget = 'fields:widget-display'

    def form_params(self):
        return self.params
