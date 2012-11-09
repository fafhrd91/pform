""" Form and Field Interfaces """
from zope import interface
from zope.interface.common import mapping
from translationstring import TranslationStringFactory

MessageFactory = _ = TranslationStringFactory('ptah.form')

FORM_INPUT = 'form-input'
FORM_DISPLAY = 'form-display'


class Invalid(Exception):
    """An exception raised by data types and validators indicating that
    the value for a particular node was not valid."""

    def __init__(self, field, msg):
        self.field = field
        self.msg = msg

    def __str__(self):
        return 'Invalid: %s: <%s>' % (self.field, self.msg)

    def __repr__(self):
        return 'Invalid(%s: <%s>)' % (self.field, self.msg)


class _null(object):
    """ Represents a null value in field-related operations. """

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__

    def __repr__(self):
        return '<widget.null>'

null = _null()


class _required(object):
    """ Represents a required value in field-related operations. """

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__

    def __repr__(self):
        return '<widget.required>'

required = _required()


class HTTPResponseIsReady(Exception):
    """ An exception raised by form update method indicates
    form should return http response """


# ----[ Vocabulary ]----------------------------------------------------------

# vocabulary/term interfaces
class ITerm(interface.Interface):
    """ term """

    value = interface.Attribute('Value')
    token = interface.Attribute('Token')
    title = interface.Attribute('Title')


class IVocabulary(interface.Interface):
    """ vocabulary """

    def get_term(value):
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source
        """

    def get_term_bytoken(token):
        """Return an ITokenizedTerm for the passed-in token.

        If `token` is not represented in the vocabulary, `LookupError`
        is raised.
        """

    def get_value(token):
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """

    def __iter__():
        """Iterate over terms."""

    def __len__():
        """Return number of terms."""

    def __contains__(value):
        """Check wether terms containes the ``value``."""

# --- API ---

def Validator(field, value):
    """
    A validator is called during field value validation.

    If ``value`` is not valid, raise a :class:`ptah.form.Invalid`
    instance as an exception after.

    ``field`` is a :class:`ptah.form.Field` instance, for use when
    raising a :class:`ptah.form.Invalid` exception.
    """


def Preview(request):
    """
    A preview is called by ``Field types`` management module.

    :param request: Pyramid request object
    :rtype: Html snippet
    """


def VocabularyFactory(context):
    """ :class:`ptah.form.fields.VocabularyField` instantiate vocabulary
    during field binding process.

    :param context: Field context
    :rtype: Vocabulary instance
    """
