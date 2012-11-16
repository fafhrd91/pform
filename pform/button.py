""" Form buttons """
import re
import sys
import binascii
from player import render
from collections import OrderedDict

AC_DEFAULT = 0
AC_PRIMARY = 1
AC_DANGER = 2
AC_SUCCESS = 3
AC_INFO = 4
AC_WARNING = 4

css = {
    AC_PRIMARY: 'btn-primary',
    AC_DANGER: 'btn-danger',
    AC_SUCCESS: 'btn-success',
    AC_INFO: 'btn-info',
    AC_WARNING: 'brn-warning'}


class Button(object):
    """A simple button in a form."""

    lang = None
    readonly = False
    alt = None
    accesskey = None
    disabled = False
    tabindex = None
    klass = 'btn'
    actype = ''

    template = 'form:submit'

    def __init__(self, name='submit', title=None, action=None, action_name=None,
                 actype=AC_DEFAULT, condition=None, extract=False, **kw):
        self.__dict__.update(kw)

        if title is None:
            title = name.capitalize()

        if isinstance(name, bytes):
            name = name.decode('utf-8')
        name = re.sub('\s', '_', name)

        self.name = name
        self.title = title
        self.action = action
        self.action_name = action_name
        self.actype = actype
        self.condition = condition
        self.extract = extract

    def __repr__(self):
        return '<{0} "{1}" : "{2}">'.format(
            self.__class__.__name__, self.name, self.title)

    def __call__(self, context):
        args = []

        if self.extract:
            data, errors = context.extract()
            if errors:
                context.add_error_message(errors)
                return

            args.append(data)

        if self.action_name is not None:
            return getattr(context, self.action_name)(*args)
        elif self.action is not None:
            return self.action(context, *args)
        else:
            raise TypeError("Action is not specified")

    def bind(self, prefix, params, context, request):
        widget = self.__class__.__new__(self.__class__)
        widget.__dict__.update(self.__dict__)

        widget.id = str(prefix + widget.name).replace('.', '-')
        widget.name = str(prefix + widget.name)
        widget.params = params
        widget.context = context
        widget.request = request
        widget.klass = '{0} {1}'.format(widget.klass, css.get(widget.actype,''))
        return widget

    def activated(self):
        return self.params.get(self.name, None) is not None

    def render(self):
        return render(self.request, self.template, self)


class Buttons(OrderedDict):
    """Form buttons manager."""

    def __init__(self, *args):
        super(Buttons, self).__init__()

        buttons = []
        for arg in args:
            if isinstance(arg, Buttons):
                buttons += arg.values()
            else:
                buttons.append(arg)

        self.add(*buttons)

    def add(self, *btns):
        """Add buttons to this manager."""
        for btn in btns:
            if btn.name in self:
                raise ValueError("Duplicate name", btn.name)

            self[btn.name] = btn

    def add_action(self, title, **kwargs):
        """Add action to this manager."""
        # Add the title to button constructor keyword arguments
        kwargs['title'] = title
        if 'name' not in kwargs:
            kwargs['name'] = create_btn_id(title)

        button = Button(**kwargs)

        self.add(button)

        return button

    def __add__(self, other):
        return self.__class__(self, other)


class Actions(OrderedDict):
    """Form actions manager."""

    prefix = 'buttons.'

    def __init__(self, form, request):
        self.form = form
        self.request = request

        super(Actions, self).__init__()

    def update(self):
        form = self.form
        params = form.form_params()

        # Create a unique prefix.
        prefix = '%s%s' % (form.prefix, self.prefix)

        # Walk through each node, making a widget out of it.
        for field in self.form.buttons.values():
            if field.condition and not field.condition(form):
                continue

            self[field.name] = field.bind(prefix, params, form, self.request)

    def execute(self):
        result = None
        executed = False
        for action in self.values():
            if action.activated():
                executed = True
                result = action(self.form)

        if executed:
            self.clear()
            self.update()

        return result


_identifier = re.compile('[A-Za-z][a-zA-Z0-9_]*$')


def create_btn_id(name):
    if _identifier.match(name):
        return str(name).lower()
    return binascii.hexlify(name.encode('utf-8'))


def _button(f_locals, title, kwargs):
    # install buttons manager
    buttons = f_locals.get('buttons')
    if buttons is None:
        buttons = Buttons()
        f_locals['buttons'] = buttons

    # create button
    btn = buttons.add_action(title, **kwargs)

    def createHandler(func):
        btn.action_name = func.__name__
        return func

    return createHandler


def button(title, **kwargs):
    """ Register new form button.

    :param title: Button title. it is beeing used for html form generations.
    :param kwargs: Keyword arguments

    .. code-block:: python

      class CustomForm(form.Form):

          field = form.Fieldset()

          @form.button('Cancel')
          def handle_cancel(self):
              ...
    """
    return _button(sys._getframe(1).f_locals, title, kwargs)


def button2(title, **kwargs):
    """ Register new form button.

    :param title: Button title. it is beeing used for html form generations.
    :param kwargs: Keyword arguments

    .. code-block:: python

      class CustomForm(form.Form):

          field = form.Fieldset()

          @form.button2('Cancel')
          def handle_cancel(self, data):
              ...
    """
    kwargs['extract'] = True
    return _button(sys._getframe(1).f_locals, title, kwargs)
