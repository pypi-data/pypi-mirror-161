from unittest import TestCase

import pytest
from bleach.css_sanitizer import ALLOWED_CSS_PROPERTIES

from pypeline.markup import ALLOWED_TAGS, ALLOWED_ATTRIBUTES
from pypeline.markup import markup

TestCase.maxDiff = None


class TestMarkup:

    def test_can_render(self):
        assert None == markup.can_render('README.cmd')
        if 'markdown' not in markup.markups_names:
            raise pytest.skip()
        else:
            assert 'markdown' == markup.can_render('README.markdown')
            assert 'markdown' == markup.can_render('README.md')

    def test_unicode_utf8(self):
        chinese = markup.unicode('華語')
        assert chinese == '華語'
        assert type(chinese) == str

    def test_unicode_ascii(self):
        ascii = markup.unicode('abc')
        assert ascii == 'abc'
        assert type(ascii) == str

    def test_unicode_latin1(self):
        latin1 = 'abcdé'.encode('latin_1')
        latin1 = markup.unicode(latin1)
        assert latin1 == 'abcdé'
        assert type(latin1) == str


class TestHTMLAllowedValues:

    def test_ALLOWED_TAGS(self):
        assert 'pre' in ALLOWED_TAGS
        assert 'button' not in ALLOWED_TAGS
        assert 'glyph' not in ALLOWED_TAGS  # svg

    def test_ALLOWED_ATTRIBUTES(self):
        assert 'alt' in ALLOWED_ATTRIBUTES['*']
        assert 'clip-path' not in ALLOWED_ATTRIBUTES['*']  # svg

    def test_ALLOWED_CSS_PROPERTIES(self):
        assert 'color' in ALLOWED_CSS_PROPERTIES
        assert 'position' not in ALLOWED_CSS_PROPERTIES
        assert '-moz-binding' not in ALLOWED_CSS_PROPERTIES