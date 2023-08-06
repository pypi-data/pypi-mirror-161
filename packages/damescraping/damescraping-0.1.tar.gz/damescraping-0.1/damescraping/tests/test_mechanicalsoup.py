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

import mechanicalsoup


class TestMechanicalsoup(TestCase):
    def test_basics(self):
        browser = mechanicalsoup.StatefulBrowser()
        self.assertTrue(browser.open("http://httpbin.org/"), "<Response [200]>")
        self.assertTrue(browser.get_url(), 'http://httpbin.org/')
        self.assertTrue(browser.follow_link("forms"), "<Response [200]>")
        self.assertTrue(browser.get_url(), 'http://httpbin.org/forms/post')
        self.assertTrue(browser.get_current_page().find_all('legend'), ["<legend> Pizza Size </legend>", "<legend> Pizza Toppings </legend>"])

    # def test_links(self):
    #     # Connect to duckduckgo
    #     browser = mechanicalsoup.StatefulBrowser()
    #     browser.open("https://duckduckgo.com/")
    #     # Fill-in the search form
    #     browser.select_form('#search_form_homepage')
    #     browser["q"] = "MechanicalSoup"
    #     browser.submit_selected()
    #     # Display the results
    #     links = []
    #     for link in browser.get_current_page().select('a.result__a'):
    #         links.append(link.text + '->' + link.attrs['href'])
    #     self.assertTrue(len(links) > 10)
