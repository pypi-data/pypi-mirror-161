"""
Ketabonline.com contains a large amount of books,
including from al-Maktaba al-Shamela al-Dhahabiyya
"""

import requests


def download_file(url, filepath):
    """
    Write the download to file in chunks,
    so that the download does not fill up the memory.
    See http://stackoverflow.com/a/16696317/4045481
    """
    r = requests.get(url, stream=True)
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

if __name__ == "__main__":
    last_pages = [92,]
    last_vol = 1
    url = "https://ketabonline.com/ar/books/106403/read?part={}&page={}"
    for vol in range(1, last_vol+1):
        for page in range(1, last_pages[vol-1]+1):
            outfp=outfolder("")
