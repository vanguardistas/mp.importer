from __future__ import unicode_literals

from unittest import TestCase
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

class CleanerTest(TestCase):

    def clean(self, dirty, context=None):
        if context is None:
            context = Mock()
        from lxml import etree
        content = '<div>{}</div>'.format(dirty)
        content = etree.XML(content)
        from .. import cleaner
        cleaner_func = getattr(cleaner, self.cleaner)
        cleaner_func(context, content)
        outstr = [content.text or '']
        for element in content.getchildren():
            outstr.append(etree.tostring(element, encoding='unicode'))
        return ''.join(outstr)

    def assertCleaned(self, dirty, clean, context=None):
        cleaned = self.clean(dirty, context=context)
        self.assertEqual(cleaned, clean)

    def assertNotCleaned(self, dirty, context=None):
        cleaned = self.clean(dirty, context=context)
        self.assertEqual(cleaned, dirty)


class Test_remove_useless_br(CleanerTest):

    cleaner = 'remove_useless_br'

    def test_first_br_inbetween_p(self):
        # we clean the first br
        self.assertCleaned(
                '<p>remove br</p><br/><p>inbetween paragraphs</p>',
                '<p>remove br</p><p>inbetween paragraphs</p>')
        self.assertCleaned(
                '<p>remove br</p>before br<br/><p>inbetween paragraphs</p>',
                '<p>remove br</p>before br<p>inbetween paragraphs</p>')
        self.assertCleaned(
                '<p>remove br</p><br/>after br<p>inbetween paragraphs</p>',
                '<p>remove br</p>after br<p>inbetween paragraphs</p>')
        self.assertCleaned(
                '<p>remove multiple br</p><br/><br/><p>inbetween paragraphs</p>',
                '<p>remove multiple br</p><p>inbetween paragraphs</p>')
        self.assertCleaned(
                '<p>remove br</p>a<br/>\n<p>inbetween paragraphs with whitespace</p>',
                '<p>remove br</p>a\n<p>inbetween paragraphs with whitespace</p>')
        self.assertCleaned(
                '<p>remove br</p>\n<br/>a<p>inbetween paragraphs with whitespace</p>',
                '<p>remove br</p>\na<p>inbetween paragraphs with whitespace</p>')
        self.assertCleaned(
                'a<br/>\n<p>inbetween paragraphs with whitespace</p>',
                'a\n<p>inbetween paragraphs with whitespace</p>')
        self.assertCleaned(
                '<p>remove br</p>\n<br/>a',
                '<p>remove br</p>\na')

    def test_first_br_in_p(self):
        # we clean the first br
        self.assertCleaned(
                '<p><br/>Text<strong>text</strong></p>',
                '<p>Text<strong>text</strong></p>')
        # also multiples
        self.assertCleaned(
                '<p><br/><br/>Text<strong>text</strong></p><h4><br/>Heading</h4>',
                '<p>Text<strong>text</strong></p><h4>Heading</h4>')
        # unless there is text before it
        self.assertNotCleaned('<p>pre<br/>Text<strong>text</strong></p>')
        # or it is at the start of an inline tag
        self.assertNotCleaned('<strong><br/>Text<em>text</em></strong>')
        self.assertNotCleaned('<p>stuff<strong><br/>Text</strong></p>')

    def test_last_br_in_p(self):
        self.assertCleaned(
                '<p>Trailing brs get removed<br/></p>',
                '<p>Trailing brs get removed</p>')
        self.assertCleaned(
                '<p>Trailing brs <em>get</em> removed<br/></p>',
                '<p>Trailing brs <em>get</em> removed</p>')
        self.assertCleaned(
                '<p>Multiple brs get <strong>cleaned</strong> yeah<br/><br/><br/></p>',
                '<p>Multiple brs get <strong>cleaned</strong> yeah</p>')
        self.assertNotCleaned('<strong>Text<em>text</em><br/></strong>')
        self.assertNotCleaned('<p>stuff<strong>Text<br/></strong>xxx</p>')
        self.assertNotCleaned('<p>stuff<strong>Text<br/></strong><em>stuff</em></p>')
    
    def test_last_br_in_p_wrapped_by_inline(self):
        self.assertCleaned(
                '<p>Trailing brs get <em>removed<br/></em></p>',
                '<p>Trailing brs get <em>removed</em></p>')

    def test_leading_br_in_p_wrapped_by_inline(self):
        self.assertCleaned(
                '<p><em><br/>Leading</em> brs get removed</p>',
                '<p><em>Leading</em> brs get removed</p>')

    def test_wierd(self):
        self.assertNotCleaned('<p>br with <br>Text</br></p>')
        self.assertNotCleaned('<p>br with <br><em>node</em></br></p>')
