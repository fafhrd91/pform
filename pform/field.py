import logging
from collections import OrderedDict
from player import render
from pform.interfaces import _, null
from pform.interfaces import Invalid, FORM_INPUT, FORM_DISPLAY

log = logging.getLogger('pform')


class Field(object):
    """Field base class.

    ``name``: Name of this field.

    ``title``: The title of this field.  Defaults to a titleization
      of the ``name`` (underscores replaced with empty strings and the
      first letter of every resulting word capitalized).  The title is
      used by form for generating html form.

    ``description``: The description for this field.  Defaults to
      ``''`` (the empty string).  The description is used by form.

    ``validator``: Optional validator for this field.  It should be
      an object that implements the
      :py:class:`pform.interfaces.Validator` interface.

    ``default``: Default field value.

    ``missing``: Field value if value is not specified in bound value.

    ``error``:: Instance os ``pform.interfaces.Invalid`` class or None.

    ``error_msg``:: Custom error message.

    ``tmpl_widget``: The path to widget template.

    ``tmpl_input``: The path to input widget template. It should be
      compatible with pyramid renderers.

    ``tmpl_display``: The path to display widget template. It should be
      compatible with pyramid renderers.

    """

    __field__ = ''

    name = ''
    title = ''
    description = ''

    default = null
    required = True
    missing = null

    error = None
    error_msg = ''
    error_required = _('Required')
    error_wrong_type = _('Wrong type')

    request = None
    params = {}
    mode = None
    value = null
    form_value = None
    context = None

    id = None
    klass = None
    typ = None

    tmpl_widget = None
    tmpl_input = None
    tmpl_display = None

    def __init__(self, name, **kw):
        self.__dict__.update(kw)

        self.name = name
        self.title = kw.get('title', name.capitalize())
        self.description = kw.get('description', '')
        self.readonly = kw.get('readonly', None)
        self.default = kw.get('default', self.default)
        self.preparer = kw.get('preparer', None)
        self.validator = kw.get('validator', None)

    def bind(self, request, prefix, value, params, context=None):
        """ Bind field to value and request params """
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.request = request
        clone.value = value
        clone.params = params
        clone.name = '%s%s' % (prefix, self.name)
        clone.id = clone.name.replace('.', '-')
        clone.context = context
        return clone

    def set_id_prefix(self, prefix):
        self.id = ('%s%s'%(prefix, self.name)).replace('.', '-')

    def update(self):
        """ Update field, prepare field for rendering """
        if self.mode is None:
            if self.readonly:
                self.mode = FORM_DISPLAY
            else:
                self.mode = FORM_INPUT

        # extract from request
        widget_value = self.extract()
        if widget_value is not null:
            self.form_value = widget_value
            return

        # get from value
        if self.value is null:
            value = self.default
        else:
            value = self.value

        # Convert the value to one that the widget can understand
        if value is not null:
            try:
                value = self.to_form(value)
            except Invalid as err:
                value = null
                log.error("Field(%s): %s", self.name, err)

        self.form_value = value if value is not null else None

    def to_form(self, value):
        """ return value representation siutable for html widget """
        return value

    def to_field(self, value):
        """ convert form value to field value """
        return value

    def get_error(self, name=None):
        if name is None:
            return self.error

        if self.error is not None:
            return self.error.get(name)

    def validate(self, value):
        """ validate value """
        if self.typ is not None and not isinstance(value, self.typ):
            raise Invalid(self.error_wrong_type, self)

        if self.required and value == self.missing:
            raise Invalid(self.error_required, self)

        if self.validator is not None:
            self.validator(self, value)

    def extract(self):
        """ extract value from params """
        return self.params.get(self.name, null)

    def render(self):
        """ render field """
        if self.mode == FORM_DISPLAY:
            tmpl = self.tmpl_display
        else:
            tmpl = self.tmpl_input

        return render(self.request, tmpl, self,
                      view=self, value=self.form_value)

    def render_widget(self):
        """ render field widget """
        tmpl = self.tmpl_widget or 'fields:widget'
        return render(self.request, tmpl, self,
                      view=self, value=self.form_value)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class InputField(Field):

    html_type = 'text'
    html_attrs = ('id', 'name', 'title', 'lang', 'disabled', 'tabindex',
                  'lang', 'disabled', 'readonly', 'alt', 'accesskey',
                  'size', 'maxlength')

    tmpl_input = 'fields:input'
    tmpl_display = 'fields:input-display'

    def update(self):
        super(InputField, self).update()

        if self.readonly:
            self.add_css_class('disabled')

    def get_html_attrs(self, **kw):
        attrs = OrderedDict()
        attrs['class'] = getattr(self, 'klass', None)
        attrs['value'] = kw.get('value', self.form_value)
        for name in self.html_attrs:
            val = getattr(self, name, None)
            attrs[name] = kw.get(name, val)

        return attrs

    def add_css_class(self, css):
        self.klass = ('%s %s' % (self.klass or '', css)).strip()


class FieldFactory(Field):
    """ Create field by name. First argument name of field registered
    with :py:func:`pform.field` decorator.

    Example:

    .. code-block:: python

       @form.field('customfield')
       class CustomField(form.Field):
           ...

       # Now `customfield` can be used for generating field:

       field = form.FieldFactory(
           'customfield', 'fieldname', ...)

    """

    __field__ = ''

    def __init__(self, typ, name, **kw):
        self.__field__ = typ

        super(FieldFactory, self).__init__(name, **kw)

    def bind(self, request, prefix, value, params, context=None):
        try:
            cls = request.registry['pform:field'][self.__field__]
        except KeyError:
            cls = None

        if cls is None:
            raise TypeError(
                "Can't find field implementation for '%s'" % self.__field__)

        clone = cls.__new__(cls)
        clone.__dict__.update(self.__dict__)
        clone.request = request
        clone.value = value
        clone.params = params
        clone.name = '%s%s' % (prefix, self.name)
        clone.id = clone.name.replace('.', '-')
        clone.context = context
        return clone
