""" Grouping field """
from pform.interfaces import null
from pform.fields import RadioField
from pform.fieldset import Fieldset
from pform.composite import CompositeField
from pform.vocabulary import Term, Vocabulary


class GroupingField(CompositeField):
    """ Grouping field

    ``key_name``: Name of group key name

    ``defaults``: Build defaults for unselected groups

    ``extract_all``: Extract values for all groups

    """

    key_name = ''
    defaults = False
    extract_all = False
    tmpl_input = 'form:grouping'

    def __init__(self, *args, **kw):
        super(GroupingField, self).__init__(*args, **kw)

        voc = Vocabulary(
            *[Term(fname, fname, field.title)
              for fname, field in self.fields.items()])

        if not self.key_name:
            self.key_name = self.name

        self.fields = Fieldset(
            RadioField(
                self.key_name,
                missing = voc[0].value,
                default = voc[0].value,
                required = False,
                vocabulary = voc)) + self.fields

    def extract(self):
        value = super(GroupingField, self).extract()

        if not self.extract_all:
            group = value[self.key_name]
            if group in value:
                return {self.key_name: group, group: value[group]}
            else:
                return {self.key_name: null}

        return value
