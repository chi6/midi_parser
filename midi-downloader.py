# -*- coding: utf-8 -*-
"""
Created on Mon May  8 19:47:37 2017

@author: Celeste
"""
#IMPORTS
from lxml import html
import requests
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlretrieve
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import urljoin
from os.path import splitext

#### ONLY EDIT BELOW THIS LINE ####

# CONSTANTS
# The page to start on
STARTING_URL = '' #EDIT THIS
# Where to save the files
DESTINATION_FOLDER_PATH = '' #EDIT THIS
# Whether or not to run recursively on links found on the starting page
SCAN_CHILD_PAGES = True

#### DO NOT EDIT BELOW LINE ####

#VARIABLES
arrayOfUrlsToVisit = []
arrayOfFilesDownloaded = []
startingUrlParsed = urlparse(STARTING_URL)
startingUrlHost = startingUrlParsed.hostname

#FUNCTIONS
# Turns a nonetype into a string
def xstr(s):
    if s is None:
        return ''
    return str(s)

# Gets a an xpath element and gets the string of the href
def mapToHrefString(linkElement):
    noneLink = linkElement.get("href")
    return xstr(noneLink).strip()

def filterOutAnchors(href):
    if href:
        return href[0] != "#"
    else:
        return True
    
def filterOutFullUrl(href):
    parsedHref = urlparse(href)
    if parsedHref.hostname:
        return False
    else:
        return True
    
def zipParsed(href):
    # Download the zip contents that are .mid files
    zipurl = urljoin(STARTING_URL, href)
    with urlopen(zipurl) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            for file in zfile.namelist():
                if file.endswith(".mid"):
                    print("extracting: " + file)
                    zfile.extract(file, DESTINATION_FOLDER_PATH)
    return
    
def pageParsed(href):
    # Set up the full URL
    fullHref = urljoin(STARTING_URL, href)
    if fullHref in arrayOfUrlsToVisit:
        # As this has already been added to the list, don't add it again
        return
    # Add the URL to the list on items we need to visit
    arrayOfUrlsToVisit.append(fullHref) 

def midParsed(href):
    # Set up the full URL
    fullHref = urljoin(STARTING_URL, href)
    if fullHref in arrayOfFilesDownloaded:
        # As this has already been added to the list, don't add it again
        return
    # Add the URL to the list on items we need to download
    arrayOfFilesDownloaded.append(fullHref) 
    return

def parsePage(url):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    linkElements = tree.xpath('//a')

    # Turn the elements into href strings
    hrefs = map(mapToHrefString, linkElements)
    # Filter out empty strings
    hrefs = filter(None, hrefs)
    # Filter out anchor tags
    hrefs = filter(filterOutAnchors, hrefs)
    # Filter anything with a scheme 
    hrefs = filter(filterOutFullUrl, hrefs)
    
    for href in hrefs:
        root, ext = splitext(href)
        if ext in FILE_EXTENSION_FUNCTIONS:
            FILE_EXTENSION_FUNCTIONS[ext](href)
    return

# DICTIONARIES
# Map the inputs to the function blocks
FILE_EXTENSION_FUNCTIONS = {
        ".htm" : pageParsed,
        ".html" : pageParsed,
        ".mid" : midParsed,
        ".zip" : zipParsed,
}

#MAIN
#Start with the main URL
parsePage(STARTING_URL)

#Create a loop that parses all URLs in the URL list, as that list grows
if SCAN_CHILD_PAGES:
    i = 0  
    while i < len(arrayOfUrlsToVisit):
        parsePage(arrayOfUrlsToVisit[i]) 
        i += 1     

#Download all the files once we have a complete list
j = 0  
while j < len(arrayOfFilesDownloaded):
    fileName = arrayOfFilesDownloaded[j].rsplit('/', 1)[-1]
    print('downloading file: ' + fileName)
    urlretrieve(arrayOfFilesDownloaded[j], DESTINATION_FOLDER_PATH + '/' + fileName)
    j += 1
print(arrayOfFilesDownloaded)
