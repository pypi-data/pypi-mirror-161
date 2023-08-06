"""Convert Manchester library html to OpenITI mARkdown.

This script subclasses the generic MarkdownConverter class
from the html2md module (based on python-markdownify,
https://github.com/matthewwithanm/python-markdownify),
which uses BeautifulSoup to create a flexible converter.

The subclass in this module, ManchesterHtmlConverter,
adds methods specifically for the conversion of books from
the Manchester collection of Arabic commentaries to Hippocratic Aphorisms
to OpenITI mARkdown.

Inheritance schema of the ManchesterHtmlConverter:

======================== ==========================
MarkdownConverter        ManchesterHtmlConverter
======================== ==========================
Options                  (inherited)
DefaultOptions           (inherited)
__init__                 (inherited)
__getattr__              (inherited)
convert                  (inherited)
process_tag              (inherited)
process_text             (inherited)
fill_out_columns         (inherited)
post_process_md          post_process_md (appended)
should_convert_tag       (inherited)
indent                   (inherited)
underline                (inherited)
create_underline_line    (inherited)
convert_a                (inherited)
convert_b                (inherited)
convert_blockquote       (inherited)
convert_br               (inherited)
convert_em               (inherited)
convert_hn               (inherited)
convert_i                (inherited)
convert_img              (inherited)
convert_list             (inherited)
convert_li               (inherited)
convert_ol               (inherited)
convert_p                (inherited)
convert_table            (inherited)
convert_tr               (inherited)
convert_ul               (inherited)
convert_strong           (inherited)
                         convert_div
                         convert_anchor
                         convert_app
                         convert_rdg
                         convert_add
                         convert_gap
                         convert_note
                         convert_corr
                         convert_locus
======================== ==========================

Examples (doctests):

    Headings: h1

    >>> import html2md_Manchester
    >>> h = '<h1>abc</h1>'
    >>> html2md_Manchester.markdownify(h)
    '\\n\\n### | abc\\n\\n'

    NB: heading style is OpenITI mARkdown style by default,
        but can be set to other styles as well:

    >>> h = '<h1>abc</h1>'
    >>> html2md_Manchester.markdownify(h, md_style=UNDERLINED)
    '\\n\\nabc\\n===\\n\\n'

    >>> h = '<h1>abc</h1>'
    >>> html2md_Manchester.markdownify(h, md_style=ATX)
    '\\n\\n# abc\\n\\n'

    Paragraphs (<p>):

    >>> h = "<p>abc</p>"
    >>> html2md_Manchester.markdownify(h)
    '\\n\\n# abc\\n\\n'

    >>> h = "<p>abc</p>"
    >>> html2md_Manchester.markdownify(h, md_style=ATX)
    '\\n\\nabc\\n\\n'


    Spans without class or with an unsupported class are stripped:

    >>> h = 'abc <span>def</span> ghi'
    >>> html2md_Manchester.markdownify(h)
    'abc def ghi'

    >>> h = 'abc <span class="unknown_span_class">def</span> ghi'
    >>> html2md_Manchester.markdownify(h)
    'abc def ghi'


    Links:

    >>> h = '<a href="a/b/c">abc</a>'
    >>> html2md_Manchester.markdownify(h)
    '[abc](a/b/c)'


    Unordered lists:

    >>> h = '<ul><li>item1</li><li>item2</li></ul>'
    >>> html2md_Manchester.markdownify(h)
    '\\n* item1\\n* item2\\n\\n'

    Ordered lists:

    >>> h = '<ol><li>item1</li><li>item2</li></ol>'
    >>> html2md_Manchester.markdownify(h)
    '\\n1. item1\\n2. item2\\n\\n'

    Nested lists:

    >>> h = '<ol><li>item1</li><li>item2:<ul><li>item3</li><li>item4</li></ul></li></ol>'
    >>> html2md_Manchester.markdownify(h)
    '\\n1. item1\\n2. item2:\\n\\n\\t* item3\\n\\t* item4\\n\\t\\n\\n'

    Italics (<i> and <em> tags):

    >>> h = 'abc <em>def</em> ghi'
    >>> html2md_Manchester.markdownify(h)
    'abc *def* ghi'

    >>> h = 'abc <i>def</i> ghi'
    >>> html2md_Manchester.markdownify(h)
    'abc *def* ghi'


    Bold (<b> and <strong> tags):

    >>> h = 'abc <b>def</b> ghi'
    >>> html2md_Manchester.markdownify(h)
    'abc **def** ghi'

    >>> h = 'abc <strong>def</strong> ghi'
    >>> html2md_Manchester.markdownify(h)
    'abc **def** ghi'

    Tables:

    >>> h = '\
    <table>\
      <tr>\
        <th>th1aaa</th><th>th2</th>\
      </tr>\
      <tr>\
        <td>td1</td><td>td2</td>\
      </tr>\
    </table>'
    >>> html2md_Manchester.markdownify(h)
    '\\n\\n| th1aaa | th2 |\\n| ------ | --- |\\n| td1    | td2 |\\n\\n'

    # i.e.,
    # | th1aaa | th2 |
    # | ------ | --- |
    # | td1    | td2 |


    Divs with specific types:

    >>> h = 'abc <div n=1 type="Title_section"><p>def</p></div>'
    >>> html2md_Manchester.markdownify(h)
    'abc\\n### | \\n\\n# def\\n\\n'

    >>> h = 'abc <div n=1 type="aphorism_commentary_unit"><p>def</p></div>'
    >>> html2md_Manchester.markdownify(h)
    'abc\\n### || 1\\n\\n# def\\n\\n'

    >>> h = 'abc <div n=1 type="aphorism"><p>def</p></div>'
    >>> html2md_Manchester.markdownify(h)
    'abc\\n### ||| 1 [aphorism]\\n\\n# def\\n\\n'

    >>> h = 'abc <div n=1 type="commentary"><p>def</p></div>'
    >>> html2md_Manchester.markdownify(h)
    'abc\\n### ||| 1 [commentary]\\n\\n# def\\n\\n'

    Divs without class or with an unsupported class are stripped:

    >>> h = 'abc\
             <div>def</div>\
             ghi'
    >>> html2md_Manchester.markdownify(h)
    'abc def ghi'

    >>> h = 'abc\
             <div class="unknown_div_class">def</div>\
             ghi'
    >>> html2md_Manchester.markdownify(h)
    'abc def ghi'
"""
import re

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(path.dirname(root_folder)))
    sys.path.append(root_folder)

from openiti.new_books.convert.helper import html2md
from openiti.new_books.convert.helper.html2md import *  # import all constants!


class ManchesterHtmlConverter(html2md.MarkdownConverter):
    """Convert Manchester library html to OpenITI mARkdown."""

##    def __init__(self, **options):
##        super().__init__(**options)
##        self.class_dict = dict()
##        self.class_dict["linebreak"] = '\n'

    def post_process_md(self, text):
        """Appends to the MarkdownConverter.post_process_md() method."""
        text = re.sub(" *\n~~ *\n", "\n", text)
        text = re.sub("#end_fn(\d+)", r"\n### |EDITOR|\n\n# ENDNOTES: (Critical apparatus)\n\n# (\1):", text, count=1)
        text = re.sub("#end_fn(\d+)", r"\n# (\1):", text)

        text = super().post_process_md(text)
        text = re.sub("### \|([\r\n])", r"### | \1", text)
        return text


    def convert_div(self, el, text):
        """Convert div tags based on their type attribute

        Examples:
            Divs with specific types:

            >>> import html2md_Manchester
            >>> h = 'abc <div n=1 type="Title_section"><p>def</p></div>'
            >>> html2md_Manchester.markdownify(h)
            'abc\\n### | \\n\\n# def\\n\\n'

            >>> h = 'abc <div n=1 type="aphorism_commentary_unit"><p>def</p></div>'
            >>> html2md_Manchester.markdownify(h)
            'abc\\n### || 1\\n\\n# def\\n\\n'

            >>> h = 'abc <div n=1 type="aphorism"><p>def</p></div>'
            >>> html2md_Manchester.markdownify(h)
            'abc\\n### ||| 1 [aphorism]\\n\\n# def\\n\\n'

            >>> h = 'abc <div n=1 type="commentary"><p>def</p></div>'
            >>> html2md_Manchester.markdownify(h)
            'abc\\n### ||| 1 [commentary]\\n\\n# def\\n\\n'

            Divs without class or with an unsupported class are stripped:

            >>> h = 'abc\
                     <div>def</div>\
                     ghi'
            >>> html2md_Manchester.markdownify(h)
            'abc def ghi'

            >>> h = 'abc\
                     <div class="unknown_div_class">def</div>\
                     ghi'
            >>> html2md_Manchester.markdownify(h)
            'abc def ghi'
        """
        # get the number of the div:
        try:
            n = el["n"] + " "
        except:
            n = ""
        if "type" in el.attrs:
            if el["type"] == "Title_section":
                return "\n### | " + text
            elif el["type"] == "aphorism_commentary_unit":
                return "\n### || " + n + text
            elif el["type"] in ["aphorism", "commentary"]:
                return "\n### ||| {}[{}]\n".format(n, el["type"]) + text
        return text

    def convert_anchor(self, el, text):
        """anchors are used to refer to endnotes / critical apparatus.

        Examples:
            >>> import html2md_Manchester
            >>> h = 'abc <anchor xml:id="begin_fn1"/>def<anchor xml:id="end_fn1" /> ghi'
            >>> html2md_Manchester.markdownify(h)
            'abc * def (1) ghi'
        """
        if 'xml:id' in el.attrs:
            if el['xml:id'].startswith("end_fn"):
                return " ({}) ".format(re.findall("\d+", el['xml:id'])[0])
            elif el['xml:id'].startswith("begin_fn"):
                return " * "
        return text

    def convert_app(self, el, text):
        """Critical apparatus entries, at the end of the text

        Examples:
            >>> import html2md_Manchester
            >>> h = 'abc<app from="#begin_fn1" to="#end_fn1"><rdg wit="#A1">def</rdg></app>'
            >>> html2md_Manchester.markdownify(h)
            'abc\\n\\n### |EDITOR|\\n\\n# ENDNOTES: (Critical apparatus)\\n\\n# (1):\\n# A1: def'

            # The next instance would be converted to: 'abc\\n\\n# (1):\\n# def'

        """
        if "to" in el.attrs:
            return "\n" + el["to"] + text
        else:
            return text

    def convert_rdg(self, el, text):
        """Reading in the critical apparatus

        Examples:
            >>> import html2md_Manchester
            >>> h = 'abc<rdg wit="#A1">def</rdg>'
            >>> html2md_Manchester.markdownify(h)
            'abc\\n# A1: def'
        """
        if "wit" in el.attrs:
            return "\n# {}: ".format(el["wit"][1:]) + text
        return text

    def convert_gap(self, el, text):
        """Critical apparatus entry for omissions

        Examples:
            >>> import html2md_Manchester
            >>> h = '<rdg wit="#A1"><gap reason="omission"/></rdg>'
            >>> html2md_Manchester.markdownify(h)
            '\\n# A1: gap (omission)'
        """
        if "reason" in el.attrs:
            reason = " ({})".format(el["reason"])
        else:
            reason = ""
        return " gap"+reason

    def convert_add(self, el, text):
        """Critical apparatus entry for additions

        Examples:
            >>> import html2md_Manchester
            >>> h = '<rdg wit="#A1"><add>abc</add></rdg>'
            >>> html2md_Manchester.markdownify(h)
            '\\n# A1: addition: abc'
        """
        return " addition: " + text

    def convert_note(self, el, text):
        """Critical apparatus entry explanation

        Examples:
            >>> import html2md_Manchester
            >>> h = '<rdg wit="#A1"><add>abc</add><note>reason="scribe"</note></rdg>'
            >>> html2md_Manchester.markdownify(h)
            '\\n# A1: addition: abc (reason="scribe")'
        """
        return " ({})".format(text)

    def convert_corr(self, el, text):
        """Critical apparatus entry for editorial corrections

        Examples:
            >>> import html2md_Manchester
            >>> h = '<corr>abc</corr>'
            >>> html2md_Manchester.markdownify(h)
            '\\n# correction: abc'
        """
        if "type" in el.attrs:
            return "\n# correction: {} ({})".format(text, el.attrs["type"])
        return "\n# correction: " + text


    def convert_locus(self, el, text):
        """Convert page numbers

        Examples:
            >>> import html2md_Manchester
            >>> h = '<locus target="CB1">2a</locus>'
            >>> html2md_Manchester.markdownify(h)
            ' PageVCB1P002A '
        """
        if "target" in el.attrs:
            vol_no = el["target"]
        else:
            vol_no = "00"
        page_no = 0
        side = ""
        try:
            page_no = re.findall("\d+[aAbB]?", text)[-1]
            if page_no.endswith(("a", "A", "b", "B")):
                side = page_no[-1].upper()
                page_no = int(page_no[:-1])
            else:
                page_no = int(page_no)
        except:
            print("no page number found in", el)

        return " PageV{}P{:03d}{} ".format(vol_no, page_no, side)

    def convert_lb(self, el, text):
        return "\n~~"


def markdownify(html, **options):
    """Shortcut to the convert method of the HindawiConverter class."""
    return ManchesterHtmlConverter(**options).convert(html)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
