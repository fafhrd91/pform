""" Composite field example """
import os
from pprint import pprint
from pyramid.view import view_config
from pyramid.interfaces import IResponse
from pyramid.httpexceptions import HTTPFound

import pform

# load countries
with open(os.path.join(os.path.split(__file__)[0], 'countries.txt'), 'r') as f:
    countries = pform.Vocabulary(
        *[(k, k, v) for k, v in
          sorted((l.strip().split(' ', 1) for l in f.readlines()),
                 key=lambda item: item[1])])


@view_config(route_name='root', renderer='__main__:simple.jinja2')
def my_form_view(request):
    # form
    form = pform.Form(
        None, request,

        fields = pform.Fieldset(
            pform.TextField(
                'name', title = u'Name'),  # field title

            pform.TextField(
                'email',
                title = u'E-Mail',
                description = u'Please provide email address.',
                validator = pform.Email(), # email validator
            ),

            pform.CompositeField(
                'address',
                title = 'Address',
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
            )
        )
    )

    # form actions
    def update_handler(form, data):
        pprint(data)
        form.request.add_message('Content has been updated.')
        return HTTPFound(location='/')

    def cancel_handler(form):
        form.request.add_message('Cancel button')
        raise HTTPFound(location='/')

    form.buttons.add_action('Update', action=update_handler,
                            actype=pform.AC_PRIMARY, extract=True)
    form.buttons.add_action('Cancel', action=cancel_handler)

    # form default data
    form.content = {'title': 'Test title',
                    'address': {'city': 'Houston',
                                'country': 'KZ'},
                    'description': 'Context description'}

    res = form.update_form()
    if IResponse.providedBy(res):
        return res

    return {'view': form}


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
