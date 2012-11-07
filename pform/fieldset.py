""" Form Fieldset implementation """
from collections import OrderedDict

from pform.field import Field
from pform.validator import All
from pform.interfaces import null, Invalid, FORM_DISPLAY


class Fieldset(OrderedDict):
    """ Fieldset holds fields """

    def __init__(self, *args, **kwargs):
        super(Fieldset, self).__init__()

        self.name = kwargs.pop('name', '')
        self.title = kwargs.pop('title', '')
        self.description = kwargs.pop('description', '')
        self.prefix = '%s.' % self.name if self.name else ''
        self.lprefix = len(self.prefix)

        validator = kwargs.pop('validator', None)
        if isinstance(validator, (tuple, list)):
            self.validator = All(*validator)
        else:
            self.validator = All()
            if validator is not None:
                self.validator.validators.append(validator)

        self.append(*args, **kwargs)

    def fields(self):
        for field in self.values():
            if isinstance(field, Field):
                yield field

    def fieldsets(self):
        yield self

        for fieldset in self.values():
            if isinstance(fieldset, Fieldset):
                yield fieldset

    def append(self, *args, **kwargs):
        for field in args:
            if isinstance(field, Field):
                if field.name in self:
                    raise ValueError("Duplicate name", field.name)
                self[field.name] = field

            elif isinstance(field, Fieldset):
                if field.name in self.name:
                    self.append(*field.values())
                    self.validator.validators.extend(field.validator.validators)
                    continue
                if field.name in self:
                    raise ValueError("Duplicate name", field.name)
                self[field.name] = field

            else:
                raise TypeError("Unrecognized argument type", field)

    def select(self, *names):
        return self.__class__(*[field for name, field in self.items()
                                if name in names])

    def omit(self, *names):
        return self.__class__(*[field for name, field in self.items()
                                if name not in names])

    def validate(self, data):
        self.validator(self, data)

    def bind(self, request, data=None, params={}, context=None):
        clone = Fieldset(
            name=self.name,
            title=self.title,
            prefix=self.prefix,
            validator=self.validator.validators)

        if data is None:
            data = {}

        for name, field in self.items():
            if isinstance(field, Fieldset):
                clone[name] = field.bind(
                    request, data.get(name, None), params, context)
            else:
                clone[name] = field.bind(
                    request, self.prefix, data.get(name, null), params, context)

        clone.request = request
        clone.params = params
        clone.data = data
        return clone

    def extract(self):
        data = {}
        errors = FieldsetErrors(self)

        for fieldset in self.fieldsets():
            if fieldset is self:
                continue
            fdata, ferrors = fieldset.extract()
            data[fieldset.name] = fdata
            errors.extend(ferrors)

        for field in self.fields():
            if field.mode == FORM_DISPLAY:
                continue

            value = field.missing
            try:
                form = field.extract()

                value = field.to_field(form)
                if value is null:
                    value = field.missing

                field.validate(value)

                if field.preparer is not None:
                    value = field.preparer(value)
            except Invalid as e:
                errors.append(e)

            data[field.name[self.lprefix:]] = value

        if not errors:
            try:
                self.validate(data)
            except Invalid as e:
                errors.append(e)

        return data, errors

    def __add__(self, fieldset):
        if not isinstance(fieldset, Fieldset):
            raise ValueError(fieldset)

        return self.__class__(self, fieldset)


class FieldsetErrors(list):

    def __init__(self, fieldset, *args):
        super(FieldsetErrors, self).__init__(args)

        self.fieldset = fieldset

    @property
    def msg(self):
        r = {}
        for err in self:
            r[err.field.name] = err.msg

        return r
