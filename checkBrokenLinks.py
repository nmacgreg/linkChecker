#!/usr/bin/python 

# ChatGPT
import requests
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

def find_broken_links(url):
    """Finds broken links on the given page and all internal pages within the same domain."""
    broken_links = []
    visited = set()
    links_to_visit = [url]
    domain = urlparse(url).netloc

    while links_to_visit:
        current_url = links_to_visit.pop()
        visited.add(current_url)

        try:
            page = requests.get(current_url)
            if page.status_code == 404:
                broken_links.append((current_url, "404 Error"))
            else:
                links_to_visit.extend(
                    [link for link in get_internal_links(current_url, domain) if link not in visited]
                )
        except requests.exceptions.RequestException as e:
            broken_links.append((current_url, str(e)))

    return broken_links

# Get URL from user
input_url = input("Enter a URL to check for broken links: ")

# Find and print broken links
broken_links = find_broken_links(input_url)
if broken_links:
    print("Broken links found:")
    for link, error in broken_links:
        print(f"- {link}: {error}")
else:
    print("No broken links found.")
