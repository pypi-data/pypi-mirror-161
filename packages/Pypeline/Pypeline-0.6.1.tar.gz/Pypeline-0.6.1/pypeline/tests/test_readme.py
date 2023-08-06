import os
import pytest

from pypeline import markups
from pypeline.markup import Markup

data = {}
markup = Markup(markups)
basedir = os.path.join(os.path.dirname(__file__), 'markups')
files = os.listdir(basedir)
for f in files:
    format = os.path.splitext(f)[1].lstrip('.')
    if format == 'html':
        continue
    data[format] = f


@pytest.mark.parametrize("format", data)
def test_readme(format):
    if format not in markup.markups_names and format != 'plaintext':
        raise pytest.skip()
    readme = data[format]
    source_file = open(os.path.join(basedir, readme), encoding='utf-8')
    source = source_file.read()
    expected_file = open(os.path.join(basedir, '%s.html' % readme), encoding='utf-8')
    expected = expected_file.read()
    actual = markup.render(os.path.join(basedir, readme))
    if source != expected:
        assert source != actual, "Did not render anything."
    assert expected == actual