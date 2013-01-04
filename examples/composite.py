""" Composite field example """
import os
from pprint import pprint
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import pform

# load countries
with open(os.path.join(os.path.split(__file__)[0], 'countries.txt'), 'r') as f:
    countries = pform.Vocabulary(
        *[(k, k, v) for k, v in
          sorted((l.strip().split(' ', 1) for l in f.readlines()),
                 key=lambda item: item[1])])


# custom composit field

class AddressField(pform.CompositeField):

    title = 'Address'

    fields = (
        pform.TextField(
            'street', title='Street', missing=''),
        pform.TextField(
            'street1', title='', required=False),
        pform.ChoiceField(
            'country',
            default = 'US',
            title='Country', vocabulary=countries),
        pform.TextField(
            'city',
            title='City'),
        pform.TextField(
            'state',
            title='State', required=True),
        pform.TextField(
            'zip', title='Zip', required=True)
    )


@view_config(route_name='root', renderer='__main__:simple.jinja2')

class MyForm(pform.Form):

    # define fields for form
    fields = pform.Fieldset(

        pform.TextField(
            'name',
            title = u'Name'),  # field title

        pform.TextField(
            'email',
            title = u'E-Mail',
            description = u'Please provide email address.',
            validator = pform.Email(), # email validator
            ),

        AddressField('address'),
        )

    # form default values
    def form_content(self):
        return {'title': 'Test title',
                'address': {'city': 'Houston',
                            'country': 'KZ'},
                'description': 'Context description'}

    @pform.button('Update', actype=pform.AC_PRIMARY)
    def update_handler(self):
        data, errors = self.extract()

        pprint(data)
        pprint(errors)
        if errors:
            self.add_error_message(errors)
            return

        self.request.add_message('Content has been updated.')
        return HTTPFound(location='/')

    @pform.button('Cancel')
    def cancel_handler(self):
        self.request.add_message('Cancel button')
        raise HTTPFound(location='/')


if __name__ == '__main__':
    from pyramid.config import Configurator
    from pyramid.scripts.pserve import wsgiref_server_runner
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    config = Configurator(
        session_factory=UnencryptedCookieSessionFactoryConfig('secret'),
        settings = {'reload_templates': True},
    )

    config.add_route('root', '/')

    config.include('pform')
    config.scan(__name__)

    wsgiref_server_runner(config.make_wsgi_app(), {})
