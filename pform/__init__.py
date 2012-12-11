# pform public api

__all__ = [
    'null', 'Invalid', 'FieldsetErrors',
    'Field', 'FieldFactory', 'Fieldset',
    'field', 'fieldpreview', 'get_field_factory', 'get_field_preview',

    'Term', 'Vocabulary', 'SimpleTerm', 'SimpleVocabulary',

    'All','Function','Regex','Email','Range', 'Length','OneOf',

    'InputField', 'CompositeField',
    'VocabularyField', 'BaseChoiceField','BaseMultiChoiceField',

    'TextField','IntegerField','FloatField',
    'DecimalField','TextAreaField','FileField','LinesField','PasswordField',
    'DateField','DateTimeField','RadioField','BoolField','ChoiceField',
    'MultiChoiceField','MultiSelectField','TimezoneField',

    'Form','FormWidgets',
    'button','button2','Button','Buttons',

    'AC_DEFAULT','AC_PRIMARY','AC_DANGER','AC_SUCCESS','AC_INFO','AC_WARNING',

    'parse_date','includeme', 'reify',
]

from pyramid.decorator import reify

# validation
from pform.interfaces import null
from pform.interfaces import Invalid

# field
from pform.field import Field
from pform.field import FieldFactory

from pform.fieldset import Fieldset
from pform.fieldset import FieldsetErrors

# field registration
from pform.directives import field
from pform.directives import fieldpreview
from pform.directives import get_field_factory
from pform.directives import get_field_preview

# vocabulary
from pform.vocabulary import Term
from pform.vocabulary import Vocabulary

SimpleTerm = Term
SimpleVocabulary = Vocabulary
SimpleVocabulary.from_items = SimpleVocabulary
SimpleVocabulary.from_values = SimpleVocabulary

# validators
from pform.validator import All
from pform.validator import Function
from pform.validator import Regex
from pform.validator import Email
from pform.validator import Range
from pform.validator import Length
from pform.validator import OneOf

# helper class
from pform.field import InputField
from pform.composite import CompositeField

# fields
from pform.fields import TextField
from pform.fields import IntegerField
from pform.fields import FloatField
from pform.fields import DecimalField
from pform.fields import TextAreaField
from pform.fields import FileField
from pform.fields import LinesField
from pform.fields import PasswordField
from pform.fields import DateField
from pform.fields import DateTimeField
from pform.fields import RadioField
from pform.fields import BoolField
from pform.fields import ChoiceField
from pform.fields import MultiChoiceField
from pform.fields import MultiSelectField
from pform.fields import TimezoneField

# helper field classes
from pform.fields import VocabularyField
from pform.fields import BaseChoiceField
from pform.fields import BaseMultiChoiceField

# forms
from pform.form import Form
from pform.form import FormWidgets

# button
from pform.button import button
from pform.button import button2
from pform.button import Button
from pform.button import Buttons
from pform.button import AC_DEFAULT
from pform.button import AC_PRIMARY
from pform.button import AC_DANGER
from pform.button import AC_SUCCESS
from pform.button import AC_INFO
from pform.button import AC_WARNING

# iso date
from pform.iso8601 import parse_date


def includeme(cfg):
    cfg.include('player')
    cfg.include('pyramid_amdjs')
    cfg.include('pyramid_jinja2')

    # field
    from pform.directives import add_field
    cfg.add_directive('provide_form_field', add_field)

    # layers
    cfg.add_layer('form', path='pform:templates/')

    # scan
    cfg.scan()
