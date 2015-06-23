from unittest import TestCase

class TestSchema(TestCase):

    def is_valid(self, content):
        from ..schema import get_schema
        from lxml import etree
        schema = get_schema()
        doc = etree.XML(content)
        return schema.validate(doc)

    def test_valid(self):
        content = '<div><p>Valid</p></div>'
        self.assertTrue(self.is_valid(content))
