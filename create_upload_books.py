from pprint import pprint
import traceback

from docs_to_html import get_html
from readhtml import get_text_images

def create_book(docURL,checking=True):
    #docURL = input('Please enter a publicy accessible Google Docs sharing link: ')
    try:
        htmlData = get_html(docURL)
        pages = get_text_images(htmlData, checking)
        return pages

    except:
        print("Something's gone wrong while creating the book.")
        traceback.print_exc()
        return None

book_data = create_book("https://docs.google.com/document/d/1OVNMHjKE7fPZUvc6B_HM9zzoINyiypS2zzPwsWe5yYc/edit?usp=sharing")
print(book_data)