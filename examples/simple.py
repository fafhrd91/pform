""" Simple form """
from pprint import pprint
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import pform


@view_config(route_name='root', renderer='__main__:simple.jinja2')

class MyForm(pform.Form):

    # define fields for form
    fields = pform.Fieldset(

        pform.TextField(
            'title',
            title = u'Title'),  # field title

        pform.TextAreaField(
            'description',
            title = u'Description',
            missing = u''), # field use this value is request doesnt contain
                            # field value, effectively field is required
                            # if `missing` is not specified
        pform.TextField(
            'email',
            title = u'E-Mail',
            description = u'Please provide email address.',
            validator = pform.Email(), # email validator
            ),
        )

    # form default values
    def form_content(self):
        return {'title': 'Test title',
                'description': 'Context description'}

    @pform.button('Update', actype=pform.AC_PRIMARY)
    def update_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        pprint(data)

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
        session_factory=UnencryptedCookieSessionFactoryConfig('secret'))

    config.add_route('root', '/')

    config.include('pform')
    config.scan(__name__)

    wsgiref_server_runner(config.make_wsgi_app(), {})
