"""
Field new/custom
================

To build new field create new class and inherit from `pform.Field` class.
Basically you need override or extend following methods:

`Field.to_form` - This method converts internal value presentation to
stracture that suitable for html template.

`Field.to_field` - This method converts result of `Field.extract` method
into internal value. In most cases it is just convert html form submitted
value.

`Field.extract` - This method extracts all values related to this form from
request params. Requests params available as `Field.params` attribute.

`Field.validate` - This method validates value (result of `Field.to_field` method), and throws Invalid exception in case if validation doesnt pass

Field uses two templates to render widget:

`tmpl_input` - is rendered by `Field.render` method and renders field input html

`tmpl_widget` - is rendered by `Field.render_widget` method and renders extra
html, like label, help, error message.

In most cases `tmpl_widget` is the same for all fields,
but `tmpl_input` is different.

"""
import decimal
from pprint import pprint
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import pform


class MoneyField(pform.Field):
    """ Money field """

    tmpl_input = '__main__:simplefield.jinja2'

    def to_form(self, value):
        """ This method converts internal value presentation into
        suitable for field template. For this field we just add dollar sign """
        return '$ %s'%value

    def to_field(self, value):
        """ This method convert html form value into internal format.
        `value` is the result of `Field.extract()` method. For this
        field we checks if input value contains '$' prefix and removes it.
        """
        value = value.strip()
        if value.startswith('$'):
            value = value[1:].strip()

        if not value:
            return pform.null

        try:
            return decimal.Decimal(value)
        except Exception:
            raise pform.Invalid(
                '"${val}" is not a number', self, mapping={'val': value})

    def extract(self):
        """ This method extracts data from request params """
        return self.params.get(self.name, pform.null)

    def validate(self, value):
        """ This method validates value, value is already converted
        to internal presenetation (result of `Field.to_field` method).
        If value is not valid just throw pform.Invalid exception
        with message as first argument and field itself as second
        """
        super(MoneyField, self).validate(value)

        if value < decimal.Decimal('50.0'):
            raise pform.Invalid('Budget is too low', self)


@view_config(route_name='root', renderer='__main__:simple.jinja2')

class MyForm(pform.Form):

    fields = pform.Fieldset(
        pform.TextField(
            'title', title = u'Title'),

        MoneyField(
            'budget', required=True),
    )

    # form default values
    def form_content(self):
        return {'title': 'Test title',
                'budget': decimal.Decimal('100.0')}

    @pform.button2('Update', actype=pform.AC_PRIMARY)
    def update_handler(self, data):
        pprint(data)

        self.request.add_message('Content has been updated.')
        return HTTPFound(location='/')


if __name__ == '__main__':
    from pyramid.config import Configurator
    from pyramid.scripts.pserve import wsgiref_server_runner
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    config = Configurator(
        session_factory=UnencryptedCookieSessionFactoryConfig('secret'))

    config.add_route('root', '/')

    config.include('pform')
    config.scan(__name__)

    wsgiref_server_runner(config.make_wsgi_app(), {})
