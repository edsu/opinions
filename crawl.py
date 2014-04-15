#!/usr/bin/env python

import re
import datetime
import opinions
import requests
import urlparse

from bs4 import BeautifulSoup

def crawl():
    for term_page_url in get_term_pages():
        get_opinions(term_page_url)
        break


def get_opinions(term_page_url):
    table = get_html_table(term_page_url)
    opinion_type = _opinion_type(term_page_url)
    opinion_list = []

    for row in table:
        # slip table has an extra first column: reporter id
        if opinion_type != "slip":
            row.insert(0, None)

        name = row[3].text
        url = urlparse.urljoin(term_page_url, row[3].get("href"))
        published = datetime.datetime.strptime(row[1].text, "%m/%d/%y")

        o = opinions.Opinion(
            type = opinion_type,
            created = datetime.datetime.now(),
            published = published,
            name = name,
            url = url,
            reporter_id = row[0].text,
            docket_num = row[2].text,
            part_num = row[5].text,
            author_id = row[4].text
        )
        opinions.db.session.add(o)
        opinion_list.append(o)

    opinions.db.session.commit()

    return opinion_list


def get_term_pages():
    url = "http://www.supremecourt.gov/opinions/opinions.aspx"
    doc = _get(url)
    urls = []
    for a in doc.select('div.dslist2 ul li a'):
        urls.append(urlparse.urljoin(url, a.get('href')))
    return urls


def get_html_table(url):
    doc = _get(url)
    table = []
    for tr in  doc.select('.datatables tr'):
        row = []
        for td in tr.select('td'):
            a = td.select('a')
            if len(a) > 0: 
                row.append(a[0])
            else:
                row.append(td)
        if len(row) > 0:
            table.append(row)
    return table


def get_authors():
    url = "http://www.supremecourt.gov/opinions/definitions_c.aspx"
    doc = _get(url)
    p = doc.select('blockquote p')[0]
    authors = []
    for line in p.text.split("\n"):
        id, name = line.split(": ")
        a = opinions.Author.query.get(id)
        if not a:
            a = opinions.Author(id=id, name=name)
            opinions.db.session.add(a)
            authors.append(a)

    opinions.db.session.commit()
    return authors


def _get(url):
    headers = {"User-Agent": "Opinions <http://github.com/edsu/opinions"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return BeautifulSoup(resp.content)
    resp.raise_for_status()


def _opinion_type(url):
    if 'slipopinions' in url:
        return 'slip'
    elif 'relatingtoorders' in url:
        return 'comment'
    elif 'in-chambers' in url:
        return 'in-chambers'
    return None


if __name__ == "__main__":
    opinions.init()
    get_authors()
    crawl()
