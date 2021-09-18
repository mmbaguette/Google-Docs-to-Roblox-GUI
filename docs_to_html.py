import requests

def get_html(docURL):
    DOCUMENT_ID = "" # Google Docs document ID
    if "/" in docURL:
        for count,char in enumerate(docURL): # get document ID from shared URL
            if DOCUMENT_ID == 0:
                if char == "d" and docURL[count + 1] == "/":
                    first = docURL[count + 2:]
                    for count2,char2 in enumerate(first):
                        if char2 == "/":
                            DOCUMENT_ID = first[:count2]
                            break
            else:
                break
    else:
        DOCUMENT_ID = docURL
    htmlUrl = 'https://docs.google.com/feeds/download/documents/export/Export?id=' + str(DOCUMENT_ID) + '&exportFormat=html' # HTML export URL
    r = requests.get(htmlUrl)
    print("URL for exporting:", htmlUrl)
    HTML_Data = None

    if r.status_code != 200:
        print('You entered an invalid URL, or the sharing link is not made publicly accessible.')
        print("URL for exporting:", htmlUrl)
        return r.status_code
    else:
        HTML_Data = r.text
    return HTML_Data