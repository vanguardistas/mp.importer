from __future__ import unicode_literals

import sys
from unittest import TestCase
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

PY3 = sys.version_info[0] == 3
PY2 = sys.version_info[0] == 2

class CleanerTest(TestCase):

    def clean(self, dirty, context=None, **kw):
        if context is None:
            context = Mock()
        from lxml import etree
        content = '<div>{}</div>'.format(dirty)
        content = etree.XML(content)
        from .. import cleaner
        cleaner_func = self.cleaner
        if PY3:
            if isinstance(cleaner_func, str):
                cleaner_func = getattr(cleaner, self.cleaner)
        else:
            if isinstance(cleaner_func, basestring):
                cleaner_func = getattr(cleaner, self.cleaner)
        cleaner_func(context, content, **kw)
        outstr = [content.text or '']
        for element in content.getchildren():
            outstr.append(etree.tostring(element, encoding='unicode'))
        return ''.join(outstr)

    def assertCleaned(self, dirty, clean, context=None, **kw):
        cleaned = self.clean(dirty, context=context, **kw)
        self.assertEqual(cleaned, clean)

    def assertNotCleaned(self, dirty, context=None, **kw):
        cleaned = self.clean(dirty, context=context, **kw)
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


class Test_remove_noop_inline_elements(CleanerTest):

    cleaner = 'remove_noop_inline_elements'

    def test_remove(self):
        self.assertCleaned(
                '<p>empty <span>spans</span> do <span>get</span> <span class="big">REMOVED</span> iff<span>theyare</span>empty</p>',
                '<p>empty spans do get <span class="big">REMOVED</span> ifftheyareempty</p>')

class Test_bubble_one_up(CleanerTest):

    def cleaner(self, context, content):
        from ..cleaner import bubble_one_up
        for node in content.findall('.//bubble'):
            bubble_one_up(node)

    def test_bubble_with_tail(self):
        self.assertCleaned(
                '<p>bubbling <bubble>up</bubble> node</p>',
                '<p>bubbling </p><bubble>up</bubble><p> node</p>')

    def test_bubble_with_other_elements(self):
        self.assertCleaned(
                '<p>bubbling <em>an</em> element <bubble>up</bubble> node</p>',
                '<p>bubbling <em>an</em> element </p><bubble>up</bubble><p> node</p>')
        self.assertCleaned(
                '<p>bubbling <em>an</em> element <bubble>up</bubble> aaa <s>node</s></p>',
                '<p>bubbling <em>an</em> element </p><bubble>up</bubble><p> aaa <s>node</s></p>')
        self.assertCleaned(
                '<p>bubbling <bubble>up</bubble> aaa <s>node</s></p>',
                '<p>bubbling </p><bubble>up</bubble><p> aaa <s>node</s></p>')

    def test_bubble_with_nothing_before(self):
        self.assertCleaned(
                '<p><bubble>up</bubble>text</p>',
                '<bubble>up</bubble><p>text</p>')
        self.assertCleaned(
                '<p><bubble>up</bubble><em>em</em></p>',
                '<bubble>up</bubble><p><em>em</em></p>')

    def test_bubble_with_nothing_after(self):
        self.assertCleaned(
                '<p>text<bubble>up</bubble></p>ptail',
                '<p>text</p><bubble>up</bubble>ptail')
        self.assertCleaned(
                '<p><em>em</em><bubble>up</bubble></p>',
                '<p><em>em</em></p><bubble>up</bubble>')

    def test_bubble_with_nothing(self):
        self.assertCleaned(
                '<p><bubble>up</bubble></p>ptail',
                '<bubble>up</bubble>ptail')
        self.assertCleaned(
                '<p><bubble>up</bubble></p>',
                '<bubble>up</bubble>')

    def test_bubble_with_only_nodes(self):
        self.assertCleaned(
                '<p><bubble>up</bubble><em>em</em></p>',
                '<bubble>up</bubble><p><em>em</em></p>')
        self.assertCleaned(
                '<p><em>em</em><bubble>up</bubble></p>',
                '<p><em>em</em></p><bubble>up</bubble>')

    def test_bubble_at_top(self):
        # is a noop
        self.assertCleaned(
                '<bubble>up</bubble><p>para</p>',
                '<bubble>up</bubble><p>para</p>')

class Test_drop_node(CleanerTest):

    def cleaner(self, context, content, **kw):
        from ..cleaner import drop_node
        for node in content.findall('.//drop'):
            drop_node(node, **kw)

    def test_keep_content(self):
        self.assertCleaned(
                '<p>dropping <drop>with text and <span>with content</span> does</drop> not lose content</p>',
                '<p>dropping with text and <span>with content</span> does not lose content</p>')
        self.assertCleaned(
                '<p><s>dropping</s><drop>with text and <span>with content</span> does</drop> not lose content</p>',
                '<p><s>dropping</s>with text and <span>with content</span> does not lose content</p>')

    def test_not_keep_content(self):
        self.assertCleaned(
                '<p>dropping <drop>with text and <span>with content</span> does</drop> not lose content</p>',
                '<p>dropping  not lose content</p>',
                keep_content=False)

    def test_add_padding(self):
        self.assertCleaned(
                '<p>padding<drop>gets added at the start and at the</drop>end</p>',
                '<p>paddinggets added at the start and at theend</p>')
        self.assertCleaned(
                '<p>padding<drop>gets added at the start and at the</drop>end</p>',
                '<p>padding gets added at the start and at the end</p>',
                add_padding=True)
        self.assertCleaned(
                '<p><span>pad</span>ding<drop>gets added at the start and at the</drop>end</p>',
                '<p><span>pad</span>ding gets added at the start and at the end</p>',
                add_padding=True)
        self.assertCleaned(
                '<p><drop>padding is not added if parent has no</drop>text<drop>or node has no tail</drop></p>',
                '<p>padding is not added if parent has no text or node has no tail</p>',
                add_padding=True)

class Test_clean_content(TestCase):

    def context(self):
        from collections import namedtuple, Counter
        import uuid
        class Context(namedtuple('Context', 'slots')):

            counter = Counter()

            def uuid(self, type):
                self.counter[type] += 1
                ns = 'metropublisher.com/{}/{}'.format(type, self.counter[type])
                if PY2:
                    ns = ns.encode('ascii')
                return uuid.uuid3(uuid.NAMESPACE_DNS, ns)

            def prob(self, type, msg):
                pass

        return Context(slots=None)

    def one(self, content, context=None, **kw):
        if context is None:
            context = self.context()
        from ..cleaner import clean_content
        return clean_content(context, content, **kw)

    def test_basic(self):
        in_content = '<p>Valid</p>'
        out_content, slots, used_fallback = self.one(in_content)
        self.assertFalse(used_fallback)
        self.assertEqual(in_content, out_content)
        self.assertEqual(slots, [])

    def test_html(self):
        in_content = '<p>Valid</p>'
        out_content, slots, used_fallback = self.one(in_content, import_as='html')
        self.assertFalse(used_fallback)
        self.assertEqual(in_content, out_content)
        self.assertEqual(slots, [])

    def test_invalid(self):
        in_content = '<invalid>Valid</invalid>'
        out_content, slots, used_fallback = self.one(in_content)
        self.assertTrue(used_fallback)
        self.assertEqual(out_content, '<slot id="65e4e4f9-734c-388c-9dae-38dc78bb723b"/>')
        self.assertEqual(slots, [{'display': 'carousel',
            'media': [{'embed_code': u'<invalid>Valid</invalid>', 'type': 'embed'}],
            'relevance': 'inline',
            'uuid': '65e4e4f9-734c-388c-9dae-38dc78bb723b'}])
