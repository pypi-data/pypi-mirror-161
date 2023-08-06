#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Damescraping; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

from unittest import TestCase

import requests
from lxml import html
from pprint import pprint
import os,re

class TestRequests(TestCase):
    def test_google(self):
        res = requests.get('http://www.google.com/search?q=lala')
        self.assertTrue(len(res.text) >0)
        self.assertEqual(res.url, 'http://www.google.com/search?q=lala')

    def test_links(self):
        start_url = 'http://www.davidam.com'
        response = requests.get(start_url)
        tree = html.fromstring(response.text)
        links = tree.cssselect('a')  # or tree.xpath('//a')
        out = []
        for link in links:
            # we use this if just in case some <a> tags lack an href attribute
            if 'href' in link.attrib:
                out.append(link.attrib['href'])
        self.assertTrue(len(links) > 10)

    def test_titles(self):

        response = requests.get('http://www.davidam.com')
        tree = html.fromstring(response.text)
        title_elem = tree.xpath('//title')[0]
        title_elem = tree.cssselect('title')[0]  # equivalent to previous XPath
        self.assertTrue(title_elem.text_content(), "David Arroyo Menéndez")

        self.assertTrue(html.tostring(title_elem), '<title>David Arroyo Men&#233;ndez</title>\n    ')
        self.assertTrue(title_elem.tag, "title")
        self.assertTrue(title_elem.getparent().tag, "head")

    # def test_xpath(self):
    #     page = requests.get('http://www.davidam.com')
    #     tree = html.fromstring(page.content)
    #     boxes = tree.xpath('//div[@class="box-title"]/text()')
    #     self.assertEqual(boxes, ['Contacto | Contact', 'Master Metodología de la Investigación en Ciencias Sociales / Master in Social Research', 'Manuales | Manuals', 'Tutoriales mundo lisp / Lisp world tutorials', 'Apuntes Tutoriales / Tutorials Notes', 'Artículos Tutoriales / Tutorials Articles '])
