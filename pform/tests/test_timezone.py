import pytz
from base import BaseTestCase


class TestTimezoneField(BaseTestCase):

    def test_timezone_schema_to_form(self):
        from pform import null, TimezoneField

        typ = TimezoneField('test')

        self.assertTrue(typ.to_form(null) is null)
        self.assertEqual(typ.to_form(pytz.UTC), 'utc')

    def test_timezone_schema_to_field(self):
        from pform import null, Invalid, TimezoneField

        typ = TimezoneField('test')

        self.assertTrue(typ.to_field(null) is null)
        self.assertTrue(typ.to_field('') is null)

        # special case for 'GMT+X' timezones
        self.assertEqual(repr(typ.to_field('GMT+6')),
                         "<StaticTzInfo 'Etc/GMT+6'>")
        self.assertEqual(repr(typ.to_field('gmt+6')),
                         "<StaticTzInfo 'Etc/GMT+6'>")

        # general timezones
        self.assertEqual(repr(typ.to_field('US/Central')),
                         "<DstTzInfo 'US/Central' CST-1 day, 18:00:00 STD>")

        self.assertEqual(repr(typ.to_field('us/central')),
                         "<DstTzInfo 'US/Central' CST-1 day, 18:00:00 STD>")

        # unknown timezone
        self.assertRaises(Invalid, typ.to_field, 'unknown')
