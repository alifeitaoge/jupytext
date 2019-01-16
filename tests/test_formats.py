import pytest
from testfixtures import compare
from nbformat.v4.nbbase import new_notebook
from jupytext.formats import guess_format, divine_format, read_format_from_metadata, rearrange_jupytext_metadata
from jupytext.formats import long_form_multiple_formats, short_form_multiple_formats, update_jupytext_formats_metadata
from .utils import list_notebooks


@pytest.mark.parametrize('nb_file', list_notebooks('python'))
def test_guess_format_light(nb_file):
    with open(nb_file) as stream:
        assert guess_format(stream.read(), ext='.py') == 'light'


@pytest.mark.parametrize('nb_file', list_notebooks('percent'))
def test_guess_format_percent(nb_file):
    with open(nb_file) as stream:
        assert guess_format(stream.read(), ext='.py') == 'percent'


@pytest.mark.parametrize('nb_file', list_notebooks('sphinx'))
def test_guess_format_sphinx(nb_file):
    with open(nb_file) as stream:
        assert guess_format(stream.read(), ext='.py') == 'sphinx'


def test_divine_format():
    assert divine_format('{"cells":[]}') == 'ipynb'
    assert divine_format('''def f(x):
    x + 1''') == 'py:light'
    assert divine_format('''# %%
def f(x):
    x + 1

# %%
def g(x):
    x + 2
''') == 'py:percent'
    assert divine_format('''This is a markdown file
with one code block

```
1 + 1
```
''') == 'md'
    assert divine_format(''';; ---
;; jupyter:
;;   jupytext:
;;     text_representation:
;;       extension: .ss
;;       format_name: percent
;; ---''') == 'ss:percent'


def test_script_with_magics_not_percent(script="""# %%time
1 + 2"""):
    assert guess_format(script, '.py') == 'light'


def test_script_with_spyder_cell_is_percent(script="""#%%
1 + 2"""):
    assert guess_format(script, '.py') == 'percent'


def test_script_with_percent_cell_and_magic_is_hydrogen(script="""#%%
%matplotlib inline
"""):
    assert guess_format(script, '.py') == 'hydrogen'


def test_script_with_spyder_cell_with_name_is_percent(script="""#%% cell name
1 + 2"""):
    assert guess_format(script, '.py') == 'percent'


def test_read_format_from_metadata(script="""---
jupyter:
  jupytext:
    formats: ipynb,pct.py:percent,lgt.py:light,spx.py:sphinx,md,Rmd
    text_representation:
      extension: .pct.py
      format_name: percent
      format_version: '1.1'
      jupytext_version: 0.8.0
---"""):
    assert read_format_from_metadata(script, '.Rmd') is None


def test_update_jupytext_formats_metadata():
    nb = new_notebook(metadata={'jupytext': {'formats': 'py'}})
    update_jupytext_formats_metadata(nb, 'py:light')
    assert nb.metadata['jupytext']['formats'] == 'py:light'

    nb = new_notebook(metadata={'jupytext': {'formats': 'ipynb,py'}})
    update_jupytext_formats_metadata(nb, 'py:light')
    assert nb.metadata['jupytext']['formats'] == 'ipynb,py:light'


def test_decompress_formats():
    assert long_form_multiple_formats('ipynb') == [{'extension': '.ipynb'}]
    assert long_form_multiple_formats('ipynb,md') == [{'extension': '.ipynb'}, {'extension': '.md'}]
    assert long_form_multiple_formats('ipynb,py:light') == [{'extension': '.ipynb'},
                                                            {'extension': '.py', 'format_name': 'light'}]
    assert long_form_multiple_formats(['ipynb', '.py:light']) == [{'extension': '.ipynb'},
                                                                  {'extension': '.py', 'format_name': 'light'}]
    assert long_form_multiple_formats('.pct.py:percent') == [
        {'extension': '.py', 'suffix': '.pct', 'format_name': 'percent'}]


def test_compress_formats():
    assert short_form_multiple_formats([{'extension': '.ipynb'}]) == 'ipynb'
    assert short_form_multiple_formats([{'extension': '.ipynb'}, {'extension': '.md'}]) == 'ipynb,md'
    assert short_form_multiple_formats(
        [{'extension': '.ipynb'}, {'extension': '.py', 'format_name': 'light'}]) == 'ipynb,py:light'
    assert short_form_multiple_formats([{'extension': '.ipynb'},
                                        {'extension': '.py', 'format_name': 'light'},
                                        {'extension': '.md', 'comment_magics': True}]) == 'ipynb,py:light,md'
    assert short_form_multiple_formats(
        [{'extension': '.py', 'suffix': '.pct', 'format_name': 'percent'}]) == '.pct.py:percent'


def test_rearrange_jupytext_metadata_metadata_filter():
    metadata = {'jupytext': {'metadata_filter': {'notebook': {'additional': ['one', 'two'], 'excluded': 'all'},
                                                 'cells': {'additional': 'all', 'excluded': ['three', 'four']}}}}
    rearrange_jupytext_metadata(metadata)
    compare({'jupytext': {'notebook_metadata_filter': 'one,two,-all',
                          'cell_metadata_filter': 'all,-three,-four'}}, metadata)


def test_rearrange_jupytext_metadata_add_dot_in_suffix():
    metadata = {'jupytext': {'text_representation': {'jupytext_version': '0.8.6'},
                             'formats': 'ipynb,pct.py,lgt.py'}}
    rearrange_jupytext_metadata(metadata)
    compare({'jupytext': {'text_representation': {'jupytext_version': '0.8.6'},
                          'formats': 'ipynb,.pct.py,.lgt.py'}}, metadata)
