import string

import markdown
from hypothesis import given
from hypothesis import strategies as st

from metadock.target_formats import MetadockTargetFormatFactory


def test_target_formats__factory_lookup():
    txt_target_format = MetadockTargetFormatFactory.target_format("txt")
    assert txt_target_format.__class__.__name__ == "PlaintextTargetFormat"
    assert txt_target_format.identifier == txt_target_format.file_extension == "txt"
    assert txt_target_format.handler("my document") == "my document"

    md_html_target_format = MetadockTargetFormatFactory.target_format("md+html")
    assert md_html_target_format.__class__.__name__ == "MdPlusHtmlTargetFormat"
    assert md_html_target_format.identifier == "md+html"
    assert md_html_target_format.file_extension == "html"
    assert md_html_target_format.handler("my document") == "<p>my document</p>"


@given(rendered_document=st.text(min_size=10, max_size=1000))
def test_target_formats__plaintext(rendered_document: str):
    txt_target_format = MetadockTargetFormatFactory.target_format("txt")
    assert txt_target_format.handler(rendered_document) == rendered_document


simple_paragraph_characters = st.text(min_size=10, max_size=1000, alphabet=string.ascii_letters + "\n ")


@given(rendered_document=simple_paragraph_characters)
def test_target_formats__md_html(rendered_document: str):
    md_html_format = MetadockTargetFormatFactory.target_format("md+html")
    html_doc = markdown.markdown(rendered_document)
    assert md_html_format.handler(rendered_document) == html_doc
