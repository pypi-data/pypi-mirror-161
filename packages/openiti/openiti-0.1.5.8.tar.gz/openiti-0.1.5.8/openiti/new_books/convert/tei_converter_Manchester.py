"""A converter for converting Manchester tei xml files into OpenITI format.

The converter has two main functions:
* convert_file: convert a single html file.
* convert_files_in_folder: convert all html files in a given folder

Usage examples:
    >>> from tei_converter_Manchester import convert_file, convert_files_in_folder
    >>> folder = r"test/Manchester/"
    >>> convert_file(folder+"Manchester000070.xml", dest_fp=folder+"converted/Manchester000070")
    >>> convert_files_in_folder(folder, dest_folder=folder+"converted")

Both functions use the ManchesterConverter class to do the heavy lifting.

The Manchester texts are Arabic commentaries on Hippocrates' Aphorisms,
edited and transcribed by the ERC Project ArabCommAph
(Arabic Commentaries on the Hippocratic Aphorisms,
https://cordis.europa.eu/project/id/283626, PI: Peter Pormann)


The ManchesterConverter uses the generic TeiConverter's tei2md.TeiConverter.

Schema representing the method inheritance in the ManchesterConverter:

=========================== ========================== =========================
GenericConverter            TeiConverter               ManchesterConverter
=========================== ========================== =========================
__init__                    __init__ (appended)        (inherited)
convert_files_in_folder     (inherited)                convert_files_in_folder
convert file                convert_file               convert_file
make_dest_fp                (inherited)                (inherited)
get_metadata (dummy)        get_metadata               (inherited)
get_data                    (inherited)                (inherited)
pre_process                 pre_process                pre-process (appended)
add_page_numbers (dummy)    (inherited - not used)     (inherited - not used)
add_structural_annotations  add_structural_annotations (inherited)
remove_notes (dummy)        (inherited - generic!)     (inherited - generic!)
reflow                      (inherited)                (inherited)
add_milestones (dummy)      (inherited - dummy)        (inherited - not used)
post_process                post_process               post-process (appended)
compose                     (inherited)                (inherited)
save_file                   (inherited)                (inherited)
                            preprocess_page_numbers    (inherited)
                            preprocess_wrapped_lines   (inherited)
=========================== ========================== =========================

##Examples:
##    >>> from tei_converter_Manchester import ManchesterConverter
##    >>> conv = ManchesterConverter(dest_folder="test/Manchester/converted")
##    >>> conv.VERBOSE = False
##    >>> folder = r"test/Manchester"
##    >>> fn = r"Manchester000070.xml"
##    >>> conv.convert_file(os.path.join(folder, fn))

"""
import os
import re
from bs4 import BeautifulSoup

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.tei_converter_generic import TeiConverter
from openiti.new_books.convert.helper import html2md_Manchester



def convert_file(fp, dest_fp=None):
    """Convert one file to OpenITI format.

    Args:
        source_fp (str): path to the file that must be converted.
        dest_fp (str): path to the converted file. Defaults to None
            (in which case, the converted folder will be put in a folder
            named "converted" in the same folder as the source_fp)

    Returns:
        None
    """
    conv = ManchesterConverter() 
    conv.convert_file(fp, dest_fp=dest_fp)

def convert_files_in_folder(src_folder, dest_folder=None,
                            extensions=[], exclude_extensions=["yml"],
                            fn_regex=None):
    """Convert all files in a folder to OpenITI format.\
    Use the `extensions` and `exclude_extensions` lists to filter\
    the files to be converted.

    Args:
        src_folder (str): path to the folder that contains
            the files that must be converted.
        dest_folder (str): path to the folder where converted files
            will be stored.
        extensions (list): list of extensions; if this list is not empty,
            only files with an extension in the list should be converted.
        exclude_extensions (list): list of extensions;
            if this list is not empty,
            only files whose extension is not in the list will be converted.
        fn_regex (str): regular expression defining the filename pattern
            e.g., "-(ara|per)\d". If `fn_regex` is defined,
            only files whose filename matches the pattern will be converted.

    Returns:
        None
    """
    conv = ManchesterConverter()
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################






class ManchesterConverter(TeiConverter):


    def pre_process(self, text):
            
        text = super().pre_process(text)
        # remove zero-width joiner:
        text = re.sub(r"‌", "", text)
        text = re.sub("([\n ])[|*] ", r"\1", text)
        text = re.sub('>', "> ", text)
        text = re.sub(" +", " ", text)
        return text

##    def convert_files_in_folder(self, folder):
##        for fn in os.listdir(folder):
##            fp = os.path.join(folder, fn)
##            if os.path.isfile(fp) and fn.endswith("ara1"):
##                self.convert_file(fp)

    def add_structural_annotations(self, text, **options):
        soup = BeautifulSoup(text, "xml")
        text_soup = soup.find("text")
        text = html2md_Manchester.markdownify(str(text_soup), **options)
        return text

    def convert_file(self, source_fp, dest_fp=None):
        """Convert one file to OpenITI format.

        Args:
            source_fp (str): path to the file that must be converted.
            dest_fp (str): path to the converted file. Defaults to None
                (in which case, the converted folder will be put in a folder
                named "converted" in the same folder as the source_fp)

        Returns:
            None
        """
        if self.VERBOSE:
            print("converting", source_fp)
        if dest_fp == None:
            dest_fp = self.make_dest_fp(source_fp)
        with open(source_fp, mode="r", encoding="utf-8") as file:
            text = file.read()
        text = self.pre_process(text)
        soup = BeautifulSoup(text, "xml")
        self.metadata = self.get_metadata(text)
        text = self.add_structural_annotations(text, strip=["note"])

        # remove notes:
        notes = ""
        #text, notes = self.remove_notes(text)
        
        if not soup.find_all("lb") and not soup.find_all(title="linebreak"):
            text = self.reflow(text)
        text = self.post_process(text)
        text = self.compose(self.metadata, text, notes)

        self.save_file(text, dest_fp)

    def post_process(self, text, verbose=False):
        text = super().post_process(text)

        # sections in unformatted texts:
        text = re.sub("(\[فصل\W+رقم\W+\d+\])", r"\n### || \1\n# ", text)

        # unformatted page and footnote numbers:
        text = re.sub("\*(\d+)\*", r" (\1)", text)
        text = re.sub("#(?![# ])", "* ", text)
        for page_bracket in re.findall(r"\[[^\]]+\]", text):
            page_nos = []
            for el in re.split("[;\-] ?", page_bracket[1:-1]):
                s = re.split("[ :.]+", el.strip())
                if len(s) == 2:
                    vol_no, page_no = s
                    #print(vol_no, page_no)
                    page_nos.append(" PageV{}P{} ".format(vol_no, page_no.upper()))
            if page_nos:
                text = text.replace(page_bracket, " ".join(page_nos))
        #for i, w in enumerate(self.witnesses):
        #    text = re.sub("PageV"+w, "PageVW{}".format(i+1), text)
            
        # pad page numbers with zeroes:
        text = re.sub(r"(PageV[^P]+P)(\d)(\D)", r"\g<1>{}\2\3".format("00"), text)
        text = re.sub(r"(PageV[^P]+P)(\d\d)(\D)", r"\g<1>{}\2\3".format("0"), text)
                    
        text = re.sub("# Page(V\d+P\d+)", r"Page\1\n\n#", text)

        text = re.sub("\n~~ *(PageV\d+P\d+)\n", r"\n\n\1\n", text)
        text = re.sub("\n~~ ", r"\n~~", text)
        text = re.sub("(### \|+[^#]+)\n~~", r"\1 ", text)
        text = re.sub("(### \|+ \[[^\]]+\]) *\n+### \|{3}", r"\1", text)
        text = re.sub("([^.؟])\n{2}# (PageV\d+P\d+) ?", r"\1 \2\n~~", text)
        # if a page number does not follow a dot/question mark
        text = re.sub("([^.؟])\n{2}(PageV\d+P\d+)\n+# ", r"\1 \2\n~~", text)
        text = re.sub("([^.؟])\n{2}(PageV\d+P\d+) *(?!\n)", r"\1 \2\n~~", text)
        return text



###########################################################################


def list_all_tags(folder, header_end_tag="</teiHeader>"):
    """
    Extracts a list of all tags used in the texts in a folder:

    For Manchester:

    <body>
    <div1 type="" n="" (name="")(/)>     # book subdivision level 1
    <div2 type="" n="" (name="")(/)>     # book subdivision level 2 
    <head>                               # title
    <lb(/)>                              # start of new line
    <milestone unit="" n=""/>            #
    <p>                                  # paragraph
    <pb (type="") n=""/>                 # start of new page
    <quote type="" (author="") (id="")>  # quotation of a source
    <text lang="" id="">                 # metadata

    # tables: 
    <table>
    <tr>
    <td>

    # line groups (e.g., for poetry):
    <lg>                                 # line group
    <l>                                  # line in line group


    div types:

    ================= =================== 
    div1              div2
    ================= ===================
    book
    books
    chapter           chapter
    folio
    sentence          sentence
                      aphorism
    ================= ===================

    pb types: primary, secondary

    quote types: lemma, commentary

    milestone units: book, ed1chapter, ed1page, ms1folio
    """
    tags = []
    full_tags = []
    for fn in os.listdir(folder):
        fp = os.path.join(folder, fn)
        #if not fn.endswith("yml") and not fn.endswith("py"):
        if fn.endswith("xml"):
            print(fn)
            with open(fp, mode="r", encoding="utf-8") as file:
                text = file.read()
    ##        orig_len = len(text)
            text = re.sub("\n~~", " ", text)
            if header_end_tag:
                text = re.sub(".+?{}".format(header_end_tag), "", text,
                              count=1, flags=re.DOTALL)
    ##        if "teiHeader" in text:
    ##            print(fn, "missing teiheader closing tag?")
    ##        if len(text) == orig_len:
    ##            print(fn, "missing teiheader?")
            text_full_tags = re.findall("<[^/][^>]*>", text)
            text_tags = re.findall("<[^/][^ >]+", text)
##            if '<milestone' in text_tags:
##                print("milestone in", fn)
##                input()
            for tag in set(text_tags):
                if tag not in tags:
                    tags.append(tag)
            for tag in set(text_full_tags):
                if tag not in full_tags:
                    full_tags.append(tag)

    stripped_tags = [re.sub('(author|lang|n|name|id)="[^"]+"', r'\1=""', tag)\
                     for tag in full_tags]
    stripped_tags = list(set(stripped_tags))

##    for tag in sorted(stripped_tags):
##        print(tag)
    for tag in sorted(full_tags):
        print(tag)


##############################################################################

if __name__ == "__main__":
##    conv = ManchesterConverter(dest_folder="test/converted")
##    conv.VERBOSE = False
##    folder = r"test"
##    fn = r"Manchester000070"
##    conv.convert_file(os.path.join(folder, fn))
##    input("passed test")
    import doctest
    doctest.testmod()

    input("Passed tests. Press Enter to start converting")
  

    folder = r"G:\London\OpenITI\RAWrabica\RAWrabica005000\Manchester"
    conv = ManchesterConverter(os.path.join(folder, "converted"))
    conv.extension = ""
    conv.convert_files_in_folder(folder)
