#!/usr/bin/python 

import sys
import os
import requests
import unittest
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def get_internal_links(url, domain):
    """Returns all internal links on the given page within the same domain."""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            href = urljoin(url, href)
            if urlparse(href).netloc == domain:
                links.append(href)
    return links

def find_broken_links(links_to_visit, visited, broken_links, domain):
    """Finds broken links on the given page and all internal pages within the same domain."""
    internal_links = []

    while links_to_visit:
        current_url = links_to_visit.pop()
        if current_url in visited:
            continue                    # we've already processed it; nothing to see
        visited.add(current_url)        # Add it to the list, so we don't visit again!

        if os.getenv("DEBUG") == "1":
            print("Visiting:", current_url)

        try:
            page = requests.get(current_url)
            if page.status_code == 404:
                continue                                                # if the current page can't be found... DO NOTHING, GO ROUND THE LOOP AGAIN
                #if current_url not in broken_links:
                    # push(broken_links[current_url], )
                    #broken_links[current_url] = []
                #broken_links[current_url].append("404 Error")           # This is one root of the problem! 
            else:
       #         links_to_visit.extend(
       #             [link for link in get_internal_links(current_url, domain) if link not in visited]
       #         )
                # We've found a valid page! You've already visted it - now parse it to get the list of links on this page
                soup = BeautifulSoup(page.content, 'html.parser')       
                links = []
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        href = urljoin(current_url, href)               # WHAAAAT ? OK, "make a valid URL by combining the current_url, with the contents of the href, which might be a relative link
                        if urlparse(href).netloc == domain:             # Only if the URL is within the original domain
                            links.append(href)
                # We have a list of all the links on this page, which are within the domain  
                for link in links:
                    if link in visited:
                        continue                                        # Did we already visit this link? Then don't visit it again!
                    visited.add(link)                                   # don't visit again
                    try:
                        # OK, this is a problem. We're visiting the page. We said we were only gonna do that once. But we're not parsing it for links
                        # Do we need to load all the "linkpage"-images into a giant datastructure & carry them all around?
                        linkpage = requests.get(link)                   
                        if linkpage.status_code == 404:                 # When we get a broken link...
                            if current_url not in broken_links:
                                broken_links[current_url] = []
                            broken_links[current_url].append(link)      # ... add it to the list of broken links found on this page!!!!! THIS IS THE PAYDIRT!
                        else:
                            # Hey, a link on the page this page is valid = do nothing
                    except requests.exceptions.RequestException as e:   # The visit to the linked URL might end in error
                        if current_url not in broken_links:
                            broken_links[current_url] = []
                        broken_links[current_url].append(link)          # This is also PAYDIRT, finding a 500 error!!

                # Wait... we've processed all the links in this page? 

        except requests.exceptions.RequestException as e:               # 
            if current_url not in broken_links:
                broken_links[current_url] = []
            broken_links[current_url].append(str(e))            

        


    return broken_links

if __name__ == '__main__':
    # Get URL from command-line argument
    if len(sys.argv) != 2:
        print("Usage: python broken_links.py <URL>")
        sys.exit(1)

    input_url = [ sys.argv[1] ]

    # Find and print broken links
    visited = [];
    domain = urlparse(input_url[0]).netloc
    broken_links = {}
    find_broken_links(input_url, visited, broken_links, domain)
    if broken_links:
        print("Broken links found:")
        print(broken_links)

        for url, errors in broken_links:
            print(f"\nURL: {url}")
            for error in errors:
                print(f"- {error}")
else:
    print("No broken links found.")

