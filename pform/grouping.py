""" GroupingField """
from player import render
from pform.interfaces import null, Invalid
from pform.fields import RadioField
from pform.fieldset import Fieldset
from pform.composite import CompositeField
from pform.composite import CompositeError
from pform.vocabulary import Term, Vocabulary


class GroupingField(CompositeField):
    """ Grouping field

    ``key_name``: Name of group key name

    """

    key_name = ''

    extract_all = False

    def __init__(self, name, **kw):
        super(GroupingField, self).__init__(name, **kw)

        voc = Vocabulary(
            *[Term(fname, fname, field.title)
              for fname, field in self.fields.items()])

        if not self.key_name:
            self.key_name = name

        self.fields = Fieldset(
            RadioField(
                self.key_name,
                missing = voc[0].value,
                default = voc[0].value,
                required = False,
                vocabulary = voc)) + self.fields

    def render_widget(self):
        if self.tmpl_input is None:
            tmpl = self.tmpl_widget or 'form:widget-grouping'
        else:
            tmpl = self.tmpl_widget or 'form:widget'

        return render(self.request, tmpl, self,
                      view=self, value=self.form_value)

    def extract(self):
        value = super(GroupingField, self).extract()

        if not self.extract_all:
            group = value[self.key_name]

            return {self.key_name: group, group: value[group]}

        return value
