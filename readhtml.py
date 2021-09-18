import re
from PIL import Image
import imagehash
import requests
from bs4 import BeautifulSoup
import traceback
import io

class GoogleHTML():
    def __init__(self, data):
        self.pages = []
        self.images = {}
        soup = BeautifulSoup(data, 'html.parser')
        bodyElements = soup.find('body').findAll(['p', 'img'])
        last_ending = 0

        for count, element in enumerate(bodyElements):
            if element.name.lower() == "p":
                if element.text.lower().startswith("!end"):
                    pageText = ""
                    page = bodyElements[last_ending:count]

                    for pageElement in page: # create the page by adding all the text before "!end" into one string
                        if pageElement.name.lower() == "img":
                            if count in self.images: # if there's already a list of images for that page
                                self.images[len(self.pages)].append(pageElement["src"])
                            else:
                                self.images[len(self.pages)] = []
                                self.images[len(self.pages)].append(pageElement["src"])
                        if pageElement.name.lower() == "p":
                            if not pageElement.text.lower().startswith("!end"): # we don't want the reader to see "!end" for no reason
                                pageText += str("\n" + pageElement.text)

                    self.pages.append(pageText)
                    last_ending = count

    def getPageText(self,page):
        return self.pages[page]

    def getNumPages(self):
        return len(self.pages)

    def getImages(self, page):
        return self.images

def similar(img1:Image,img2:Image,cutoff=5):
    hash1 = imagehash.average_hash(img1)
    hash2 = imagehash.average_hash(img2)
    if hash1 - hash2 < cutoff:
        return True
    else:
        return False

def get_text_images(data,checking=True): # return dict of pages containing images from the given PDF file data
    #pdf_data = io.BytesIO(data)
    doc = GoogleHTML(data) # PDF file reader object
    pages = dict()
    pages["output"] = ""

    for i in range(doc.getNumPages()): # loop through each page and find decals, text genre, author etc
        text = doc.getPageText(i) # page text
        decalIds = []
        openSquareBracket = text.find("[") # first instance of square brackets in the page's text
        closedSquareBracket = text.find("]")

        if openSquareBracket >= 0: # if there's even decals at all
            decalIds = text[openSquareBracket:closedSquareBracket].split(",")
            decalIds = [''.join(e for e in d if e.isalnum()) for d in decalIds]
            text = text[:openSquareBracket - 1]

        if i == 0: # if it's the first page of the PDF
            line = text.rfind("━") # find last occurence of this line character

            if line >= 0: # is there even a line character?
                text = text[line:] # remove everything before it
            else:
                print("Could not find line character ━━━━━")

            robloxSearchResults = re.search('Author:(.+?)\n', text) # finding author username
            roblox = ""
            if robloxSearchResults: # if it found any results
                roblox = robloxSearchResults.group(0).strip(' \t\n\r')[7:].replace(" ","") # strip whitespace from roblox username
            else:
                print("Could not find the Author username!")

            genreSearchResults = re.search('Genre:(.+?)\n', text) # finding genre
            genre = ""
            if genreSearchResults: # if it found any results
                genre = genreSearchResults.group(0).strip(' \t\n\r')[6:].replace(" ","")
            else:
                print("Could not find the genre!")

            titleSearchResults = re.search('Title:(.+?)\n', text) # finding title
            title = ""
            if titleSearchResults: # if it found any results
                title = titleSearchResults.group(0).strip('\t\n\r')[7:]
            else:
                print("Could not find the title!")

            coverSearchResults = re.search('Cover:(.+?)\n', text) # finding cover
            cover = ""
            if coverSearchResults: # if it found any results
                cover = coverSearchResults.group(0).strip('\t\n\r')[7:]
            else:
                print("Could not find the cover!")

            text = text[max([result.end() for result in [titleSearchResults, coverSearchResults, genreSearchResults, robloxSearchResults] if result]):]

        for count, chr in enumerate(text):
            if chr != "\n":
                text = text[count:]
                break

        images = doc.getImages(i) # returns list of image URLs in page

        if len(images) > 0 and len(decalIds) > 0 and checking:  # if we're making sure that the images on the user's doc are the same as the specified decal IDs
            for pageNumber in images:
                for imgUrl in images[pageNumber]:
                    print("Img link:",imgUrl)
                    m = requests.get(imgUrl)

                    if m.status_code == 200:
                        img1 = Image.open(io.BytesIO(m.content))

                        try:
                            imagesSimilar = False

                            decalIdsCopy = decalIds.copy()
                            for decalId in decalIds: # if we can match each decal ID from that page with at least 1 image on the same page
                                r = requests.get('https://rprxy.xyz/asset-thumbnail/image?width=420&height=420&format=png&assetId=' + decalId)

                                if r.status_code == 200:
                                    img2 = Image.open(io.BytesIO(r.content))

                                    if similar(img1,img2):
                                        print('images are similar (' + decalId + ')')
                                        imagesSimilar = True
                                    else:
                                        print('images are not similar (' + decalId + ')')
                                else:
                                    print('Decal ID not found or could not reach rprxy.xyz site')
                                    pages["ouput"] = pages["output"] + "\nDecal ID not found or could not reach Roblox site"
                                    imagesSimilar = False
                                    break

                            if not imagesSimilar:
                                decalIdsCopy.remove(decalId)
                                pages["ouput"] = pages["output"] + "\nImages are not similar (" + decalId + ")"
                            decalIds = decalIdsCopy

                        except:
                            pages["ouput"] = pages["output"] + "\nCould not find the original decal \'" + decalId + "\' to compare it, or could not reach Roblox site."
                            print('Could not find the original decal \"' + decalId + "\" to compare it")
                            print(traceback.format_exc())
                            return pages["ouput"]

        pages["Page " + str(i + 1)] = {
            "text": text,
            "decals": decalIds,
        }
        pages["roblox"] = roblox
        pages["genre"] = genre
        pages["title"] = title
        pages["cover"] = cover
    return pages