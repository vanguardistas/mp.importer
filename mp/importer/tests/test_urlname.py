# -*- coding: utf-8 -*-

from unittest import TestCase

class Test_urlname_suggester(TestCase):

    def assertSuggestion(self, input, suggestion, language='en'):
        from ..urlname import urlname_suggester
        rslt = urlname_suggester(input, language=language)
        self.assertEqual(suggestion, rslt)

    def test_nonlatin(self):
        self.assertSuggestion(u'Ψάπφω', 'psappho')
        self.assertSuggestion(u'中文', 'zhong-wen')

    def test_reserved(self):
        self.assertSuggestion(u'sl/ash', 'sl-ash')
        self.assertSuggestion(u'da-----sh', 'da-sh')
        self.assertSuggestion(u'da - sh', 'da-sh')
        self.assertSuggestion(u'!@#$%^"', '-')

    def test_stopwords_en(self):
        self.assertSuggestion(u'A cat sat on the mat', 'cat-sat-mat')

    def test_stopwords_de(self):
        self.assertSuggestion(u'Der alte Mann und das Meer', 'alte-mann-meer', language='de')
        self.assertSuggestion(u'Über Mann', 'mann', language='de')
