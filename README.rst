pform
=====

.. image :: https://travis-ci.org/fafhrd91/pform.png
  :target:  https://travis-ci.org/fafhrd91/pform


Simple form example
-------------------

Form contains three different subsystems, basic form attributes, fields and actions.

.. code-block:: python

    import pform
    from pyramid.httpexceptions import HTTPFound


    class EditForm(pform.Form):

         label = 'Edit form'

         fields = pform.Fieldset(
             pform.TextField(
                'name', title='Name')
         )

         @pform.button('Save')
         def safe_handler(self):
             data, errors = self.extract()

             if errors:
                 self.add_error_message(errors)

             self.context.name = data['name']

         @pform.button('Cancel')
         def cancel_handler(self):
             return HTTPFound(location='.')

This form renders one field `name` and two actions `safe` and `cancel` (submit buttons). Now we can render this form:

.. code-block:: python

    from pyramid.view import view_config

    @view_config(route_name='....', renderer='myview.jinja2')
    def my_view(request):
        form = EditForm(some_context, request)
        return form()

also it is possible to use form class as view:

.. code-block:: python

    @view_config(route_name='....')
    class EditForm(pform.Form):

        fields = ...


To do additional custom form initialization just override `update` method, also
if `update` method returns dictionary this values bypasses to form template:

.. code-block:: python

   class EditForm(pform.Form):

       def update(self):
           # custom form initialization
           return {some_data: some_value}


To get form values use `extract` method, this method return
`data` and `errors`. `data` is a form result, `errors` is a list of errors:

.. code-block:: python

   class EditForm(pform.Form):

       @pform.button('Save')
       def save_handler(self):
           data, errors = self.extract()

           if errors:
               self.add_error_message(errors)

           # save data
           ...


Customization
-------------

There are two ways for field and form customization:

1. Global customization 

  `pform` library uses `player`::https://github.com/fafhrd91/pform/tree/master/examples library for customization. `pform` libriary defines layer category `form` for all templates.


2. Field/form customization

  Also it is possible to customize widget of input template for each field. You can pass ``tmpl_widget`` argument to to field constructor for widget customization and ``tmpl_input`` argument for input generation. Both arguments should be valid pyramid renderer path.
  Form accepts three different templates, ``tmpl_view``, ``tmpl_actions`` and ``tmpl_widget``. ``tmpl_view`` is form renderer, ``tmpl_actions`` if form buttons renderer, ``tmpl_widget`` is custom field widget renderer. If field does not use custom ``tmpl_widget`` then form automatically sets ``tmpl_widget`` for each of this fields.


Examples
--------

There are several example.  You can find them in the `examples` directory at github.

https://github.com/fafhrd91/pform/tree/master/examples


Requirements
------------

- Python 2.6+ or Python 3.2+

- virtualenv



License
-------

pform is offered under the BSD license.

