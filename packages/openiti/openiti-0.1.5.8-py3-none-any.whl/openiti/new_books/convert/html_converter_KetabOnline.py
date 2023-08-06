"""Converter that converts HTML files from the KetabOnline library to OpenITI mARkdown.

The converter has two main functions:
* convert_file: convert a single html file.
* convert_files_in_folder: convert all html files in a given folder

Usage examples:
    >>> from html_converter_KetabOnline import convert_file
    >>> folder = r"test/KetabOnline/"
    >>> convert_file(folder+"86596.html", dest_fp=folder+"converted/86596")
    >>> from html_converter_KetabOnline import convert_files_in_folder
    >>> convert_files_in_folder(folder, dest_folder=folder+"converted")  

Both functions use the KetabOnlineHtmlConverter class to do the heavy lifting.
The KetabOnlineHtmlConverter is a subclass of GenericHtmlConverter,
which in its turn inherits many functions from the GenericConverter.

GenericConverter
    \_ GenericHtmlConverter
            \_ KetabOnlineHtmlConverter
            \_ NoorlibHtmlConverter
            \_ ...

Overview of the methods of these classes:
(methods of GenericConverter are inherited by GenericHtmlConverter;
and methods of GenericHtmlConverter are inherited by KetabOnlineHtmlConverter.
Methods of the superclass with the same name
in the subclass are overwritten by the latter)

================================== ========================== ==========================
GenericConverter                   GenericHtmlConverter       KetabOnlineHtmlConverter
================================== ========================== ==========================
__init__                           __init__                   (inherited)
convert_files_in_folder            (inherited)                (inherited)
convert file                       (inherited)                (inherited)
make_dest_fp                       (inherited - generic!)     (inherited - generic!)
get_metadata (dummy)               (inherited - dummy!)       get_metadata
get_data                           (inherited)                (inherited)
pre_process                        (inherited)                (inherited)
add_page_numbers (dummy)           (inherited - dummy!)       add_page_numbers
add_structural_annotations (dummy) add_structural_annotations add_structural_annotations
remove_notes (dummy)               remove_notes               remove_notes
reflow                             (inherited)                (inherited)
add_milestones (dummy)             (inherited - dummy!)       (inherited - dummy!)
post_process                       (inherited - generic!)     post_process
compose                            (inherited)                (inherited)
save_file                          (inherited)                (inherited)
                                   inspect_tags_in_html       (inherited)
                                   inspect_tags_in_folder     (inherited)
                                   find_example_of_tag        (inherited)
================================== ========================== ==========================

The KetabOnlineHtmlConverter's add_structural_annotations method uses html2md_KetabOnline,
an adaptation of the generic html2md (based on markdownify)
to convert the html tags to OpenITI annotations. 

Examples:
    >>> from html_converter_KetabOnline import KetabOnlineHtmlConverter
    >>> conv = KetabOnlineHtmlConverter()
    >>> conv.VERBOSE = False
    >>> folder = r"test/KetabOnline/"
    >>> conv.convert_file(folder+"86596.html")
    >>> conv.convert_files_in_folder(folder, extensions=["html"])
"""

from bs4 import BeautifulSoup
import re
import os

if __name__ == '__main__':
    from os import sys, path
    root_folder = path.dirname(path.dirname(path.abspath(__file__)))
    root_folder = path.dirname(path.dirname(root_folder))
    sys.path.append(root_folder)

from openiti.new_books.convert.html_converter_generic import GenericHtmlConverter
from openiti.new_books.convert.helper import html2md_KetabOnline
from openiti.helper.funcs import natural_sort


def combine_html_files_in_folder(folder, dest_fp="temp"):
    text = []
    for i, fn in enumerate(natural_sort(os.listdir(folder))):
        print(fn)
        fp = os.path.join(folder, fn)
        with open(fp, mode="r", encoding="utf-8") as file:
            html = file.read()
        soup = BeautifulSoup(html, "html.parser")
        if i == 0:
            meta = soup.find_all("meta", attrs={"name":"og:description"})[0]
            [tag.extract() for tag in meta.children]
            text.append(meta.prettify())
            print(meta.prettify())

        page_text = soup.find_all("p", class_="page-content-wrapper")
        if page_text:
            #page = int(fp[:-5].split("_")[-1])
            vol = int(fp[:-5].split("_")[-2])
            try:
                page_text = re.sub("/(\d+)/",
                                   lambda m: "PageBegV{:02d}P{:03d}".format(vol, int(m.group(1))),
                                   page_text[0].prettify())
            except Exception as e:
                print(e)
                page_text = page_text[0].prettify()
##            print("---")
##            print(page_text)
##            print("***")
##            input()

            text.append(page_text)
            #text.append("PageV{:02d}P{:03d}".format(vol, page))
        
    with open(dest_fp, mode="w", encoding="utf-8") as file:
        file.write("\n\n".join(text))
    #convert_file("temp", dest_fp)
        
bk_id = 106403
folder = r"D:\London\OpenITI\new_books\ketabonline\html\{}".format(bk_id)
temp_fp = r"D:\London\OpenITI\new_books\ketabonline\html\{0}\KetabOnline_{0}_all.temp".format(bk_id)
#combine_html_files_in_folder(folder, temp_fp)

def convert_file(fp, dest_fp=None, verbose=False):
    """Convert one file to OpenITI format.

    Args:
        source_fp (str): path to the file that must be converted.
        dest_fp (str): path to the converted file.

    Returns:
        None
    """
    conv = KetabOnlineHtmlConverter()
    conv.VERBOSE = verbose
    conv.convert_file(fp, dest_fp=dest_fp)




def convert_files_in_folder(src_folder, dest_folder=None,
                            extensions=["html"], exclude_extensions=["yml"],
                            fn_regex=None, verbose=False):
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
    conv = KetabOnlineHtmlConverter()
    conv.VERBOSE = verbose
    conv.convert_files_in_folder(src_folder, dest_folder=dest_folder,
                                 extensions=extensions,
                                 exclude_extensions=exclude_extensions,
                                 fn_regex=fn_regex)


################################################################################


class KetabOnlineHtmlConverter(GenericHtmlConverter):

##    # moved this function to the generic_converter!
##    def pre_process(self, text):
##        text = super().pre_process(text)
##        # attach separated wa- and a- prefixes to the following word: 
##        text = re.sub(r"\b([وأ])[\s~]+", r"\1", text)
##        return text

    def get_metadata(self, text):
        """Gets the metadata from the first td in the html.

        The metadata in KetabOnline texts are in
        the "content" value of a meta element with name="og:description" in the title element.

        Args:
            text (str): text of the file that contains both data and metadata

        Returns:
            metadata (str): metadata formatted in OpenITI format
                (including the magic value and the header splitter)
        """
        soup = BeautifulSoup(text)
        # get the metadata description from the header:
        meta_tag = soup.find_all("meta", attrs={"name":"og:description"})[0]
        meta = meta_tag["content"].strip()
        meta_keys = re.finditer("[\w\S]+:", meta)
        meta_list = []
        prev = None
        for m in meta_keys:
            if prev:
                meta_list.append(meta[prev.start():m.start()])
            prev = m
        meta_list.append(meta[prev.start():])
        # add magic value and header splitter: 
        metadata = self.magic_value + '\n#META# ' + "\n#META# ".join(meta_list) + '\n' + self.header_splitter
        return metadata

    def add_page_numbers(self, text, source_fp):
        """Convert the page numbers in the text into OpenITI mARkdown format"""
        if re.findall("PageV\d+P\d+", text):
            return text
        try:
            vol_no = int(re.findall("V(\d+)", source_fp)[0])
            vol_no = "PageV{:02d}P{}".format(vol_no, "{:03d}")
        except:
            vol_no = "PageV01P{:03d}"
        def fmt_match(match):
            r = match.group(1) + vol_no.format(int(match.group(2)))
            return r + match.group(3)
        end = '<td class="book-page-show">|\Z'
        text = re.sub(r'(</td>)[^<\d]*(\d+)[^<]*({})'.format(end),
                      fmt_match, text)
        return text

    #def convert_html2md(self, html):
    def add_structural_annotations(self, html):
        """Convert html to mARkdown text using a html2md converter."""
        #text = html2md_KetabOnline.markdownify(html)
##        text = []
##
##        for i, p in enumerate(re.split("(\n+PageV\d+P\d+\n+)", html)):
##            if re.findall("PageV\d+P\d+", p):
##                text.append(p)
##            else:
##                soup = BeautifulSoup(p)
##                try:
##                    t = html2md_KetabOnline.markdownify(soup.td.prettify())
##                except:
##                    print("no <td> tag on this page:")
##                    print(soup.prettify())
##                    html2md_KetabOnline.markdownify(soup.prettify())
##                text.append(t)
##        text = "".join(text)
        text = html2md_KetabOnline.markdownify(html)
        return text             

    def post_process(self, text):
        print("post_processing")
        # remove footnotes (not displayed in their pages, so no way to find the page numbers):
        text = re.sub("(?:### \$ )?__FOOTNOTE__.+[\r\n]*", "", text)
        text = re.sub("@QUOTE_START@([^@]+)@QUOTE_END@",
                      lambda m: "@SRC0{}{}".format(len(re.findall("\w+", m.group(1))), m.group(1)),
                      text)
        text = re.sub("@QB@([^@]+)@QE@",
                      lambda m: "@QUR0{}{}".format(len(re.findall("\w+", m.group(1))), m.group(1)),
                      text)
        text = super().post_process(text)
        # convert kalematekhass tags at the beginning of a line to headers:
        text = re.sub("# \*\* (.+)\*\*", r"### || \1", text)
        text = re.sub("# \*\*\* (.+)\*\*\*", r"### ||| \1", text)
        # add footnotes after a title to same line as the title:
        text = re.sub("(### \|+ .+)[\r\n]+# (\[\d+\][\r\n]+)", r"\1 \2", text)
        # remove floating hashtags and pipes
        text = re.sub("[\r\n]+# *([\r\n]+)", r"\1", text)
        text = re.sub("[\r\n]+\|+ *([\r\n]+)", r"\1", text)
        
        #
        text = re.sub("([^\r\n .!؟][\r\n]+PageV[^P]+P\d+[\r\n]+)# ", r"\1~~", text)
        return text

dest_folder = r"D:\London\OpenITI\new_books\ketabonline\txt"
dest_fp = os.path.join(dest_folder, "KetabOnline{:08}.txt".format(bk_id))
convert_file(temp_fp, dest_fp)
input("CONVERTED! CONTINUE?")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    input("Passed all tests. Continue?")
    
    conv = KetabOnlineHtmlConverter()
    folder = r"G:\London\OpenITI\new\KetabOnline"
    import os
    conv.convert_file(os.path.join(folder, "10461.html"))

    conv.convert_files_in_folder(folder)
