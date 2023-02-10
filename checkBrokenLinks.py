#!/usr/bin/python 

# ChatGPT
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

def find_broken_links(url):
    """Finds broken links on the given page and all internal pages within the same domain."""
    broken_links = {}
    visited = set()
    links_to_visit = [url]
    domain = urlparse(url).netloc

    while links_to_visit:
        current_url = links_to_visit.pop()
        if current_url in visited:
            continue
        visited.add(current_url)

        if os.getenv("DEBUG") == "1":
            print("Visiting:", current_url)

        try:
            page = requests.get(current_url)
            if page.status_code == 404:
                if current_url not in broken_links:
                    broken_links[current_url] = []
                broken_links[current_url].append("404 Error")
            else:
                links_to_visit.extend(
                    [link for link in get_internal_links(current_url, domain) if link not in visited]
                )
        except requests.exceptions.RequestException as e:
            if current_url not in broken_links:
                broken_links[current_url] = []
            broken_links[current_url].append(str(e))

    return broken_links

class TestBrokenLinks(unittest.TestCase):
    def test_find_broken_links(self):
        test_data = [
            ('https://www.google.com', {}),
            ('https://www.github.com', {}),
            ('https://nonexistentwebsite.com', {'https://nonexistentwebsite.com': ['404 Client Error: Not Found for url: https://nonexistentwebsite.com']}),
        ]
        for url, expected_output in test_data:
            self.assertEqual(find_broken_links(url), expected_output)

if __name__ == '__main__':
    # Get URL from command-line argument
    if len(sys.argv) != 2:
        print("Usage: python broken_links.py <URL>")
        sys.exit(1)

    input_url = sys.argv[1]

    # Find and print broken links
    broken_links = find_broken_links(input_url)
    if broken_links:
        print("Broken links found:")
        for url, errors in broken

