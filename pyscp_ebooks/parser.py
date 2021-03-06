#!/usr/bin/env python3
"""Parse wikidot html."""

###############################################################################
# Module Imports
###############################################################################

import bs4

###############################################################################


def bs(html=''):
    return bs4.BeautifulSoup(html, 'lxml')

###############################################################################


class Parser:

    """
    Parse wikidot html code into a epub-compatible form.

    This is a class to allow inheritance by individual epub-builders.
    """

    def __init__(self, pages):
        self.pages = pages

    def parse(self, page):
        soup = bs(page.html).find(id='page-content')
        for elem in soup(class_='page-rate-widget-box'):
            elem.decompose()
        for elem in soup(class_='yui-navset'):
            self._tab(elem)
        for elem in soup(class_='collapsible-block'):
            self._collapsible(elem)
        for elem in soup('sup', class_='footnoteref'):
            self._footnote(elem)
        for elem in soup(class_='footnote-footer'):
            self._footnote_footer(elem)
        for elem in soup('blockquote'):
            self._quote(elem)
        for elem in soup('a'):
            self._link(elem, page._wiki.site)
        for elem in soup('img'):
            self._image(elem)
        self._title(soup, page)
        return str(soup)

    def _tab(self, elem):
        """Parse wikidot tab block."""
        elem.attrs = {'class': 'tabview'}
        titles = elem.find(class_='yui-nav')('em')
        elem.find(class_='yui-nav').decompose()
        elem.div.unwrap()
        for tab, title in zip(
                elem('div', recursive=False), titles):
            tab.attrs = {'class': 'tabview-tab'}
            new_title = bs().new_tag('p', **{'class': 'tab-title'})
            new_title.string = title.text
            tab.insert(0, new_title)

    def _collapsible(self, elem):
        """Parse collapsible block."""
        elem.attrs = {'class': 'collapsible'}
        title = bs().new_tag('p', **{'class': 'collapsible-title'})
        title.string = elem.find(class_='collapsible-block-link').text
        body = elem.find(class_='collapsible-block-content')
        elem.clear()
        elem.append(title)
        for child in list(body.contents):
            elem.append(child)

    def _footnote(self, elem):
        """Parse a footnote."""
        elem.string = elem.a.string

    def _footnote_footer(self, elem):
        """Parse footnote footer."""
        elem.attrs = {'class': 'footnote'}
        elem.string = ''.join(elem.stripped_strings)

    def _link(self, elem, site):
        """Parse a link; remap if links to a page, otherwise remove."""
        if 'href' not in elem.attrs:
            return
        link = elem['href']
        if not link.startswith(site):
            link = site + link
        if link not in self.pages:
            elem.name = 'span'
            elem.attrs = {'class': 'link'}
        else:
            elem['href'] = self.pages[link] + '.xhtml'

    def _quote(self, elem):
        """Parse a block quote."""
        elem.name = 'div'
        elem.attrs = {'class': 'quote'}

    def _image(self, elem):
        elem.decompose()

    def _title(self, soup, page):
        title = bs().new_tag('p', **{'class': 'title'})
        title.string = page.title
        soup.insert(0, title)
