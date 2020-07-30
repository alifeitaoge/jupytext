from nbformat.v4.nbbase import new_notebook
from jupytext.compare import compare
import jupytext
from jupytext.header import (
    uncomment_line,
    header_to_metadata,
    metadata_to_header,
)
from jupytext.formats import get_format_implementation


def test_uncomment():
    assert uncomment_line("# line one", "#") == "line one"
    assert uncomment_line("#line two", "#") == "line two"
    assert uncomment_line("#line two", "") == "#line two"


def test_header_to_metadata_and_cell_blank_line():
    text = """---
title: Sample header
---

Header is followed by a blank line
"""
    lines = text.splitlines()
    metadata, _, pos = header_to_metadata(lines, "")

    compare(metadata, {"jupytext": {"root_level_metadata": {"title": "Sample header"}}})
    assert lines[pos].startswith("Header is")


def test_header_to_metadata_and_cell_no_blank_line():
    text = """---
title: Sample header
---
Header is not followed by a blank line
"""
    lines = text.splitlines()
    metadata, _, pos = header_to_metadata(lines, "")

    compare(metadata, {"jupytext": {"root_level_metadata": {"title": "Sample header"}}})
    assert lines[pos].startswith("Header is")


def test_header_to_metadata_and_cell_metadata():
    text = """---
title: Sample header
jupyter:
  main_language: python
---
"""
    lines = text.splitlines()
    metadata, _, pos = header_to_metadata(lines, "")

    compare(
        metadata,
        {
            "main_language": "python",
            "jupytext": {"root_level_metadata": {"title": "Sample header"}},
        },
    )
    assert pos == len(lines)


def test_metadata_and_cell_to_header(no_jupytext_version_number):
    metadata = {
        "jupytext": {
            "main_language": "python",
            "root_level_metadata": {"title": "Sample header"},
        }
    }
    header = metadata_to_header(metadata, get_format_implementation(".md"), ".md")
    compare(
        "\n".join(header),
        """---
jupyter:
  jupytext:
    main_language: python
title: Sample header
---""",
    )


def test_metadata_and_cell_to_header2(no_jupytext_version_number):
    header = metadata_to_header({}, get_format_implementation(".md"), ".md")
    assert header == []


def test_notebook_from_plain_script_has_metadata_filter(
    script="""print('Hello world")
""",
):
    nb = jupytext.reads(script, ".py")
    assert nb.metadata.get("jupytext", {}).get("notebook_metadata_filter") == "-all"
    assert nb.metadata.get("jupytext", {}).get("cell_metadata_filter") == "-all"
    script2 = jupytext.writes(nb, ".py")

    compare(script2, script)


def test_multiline_metadata(
    no_jupytext_version_number,
    notebook=new_notebook(
        metadata={
            "multiline": """A multiline string

with a blank line""",
            "jupytext": {"notebook_metadata_filter": "all"},
        }
    ),
    markdown="""---
jupyter:
  jupytext:
    notebook_metadata_filter: all
  multiline: 'A multiline string


    with a blank line'
---
""",
):
    actual = jupytext.writes(notebook, ".md")
    compare(actual, markdown)
    nb2 = jupytext.reads(markdown, ".md")
    compare(nb2, notebook)


def test_header_in_html_comment():
    text = """<!--

---
jupyter:
  title: Sample header
---

-->
"""
    lines = text.splitlines()
    metadata, _, _ = header_to_metadata(lines, "")

    assert metadata == {"title": "Sample header"}


def test_header_to_html_comment(no_jupytext_version_number):
    metadata = {"jupytext": {"mainlanguage": "python", "hide_notebook_metadata": True}}
    header = metadata_to_header(metadata, get_format_implementation(".md"), ".md")
    compare(
        "\n".join(header),
        """<!--

---
jupyter:
  jupytext:
    hide_notebook_metadata: true
    mainlanguage: python
---

-->""",
    )
