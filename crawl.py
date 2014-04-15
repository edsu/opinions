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

        o = opinions.Opinion.query.filter_by(url=url).first()
        if not o:
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
    url = "http://www.supremecourt.gov/opinions/definitions.aspx"
    doc = _get(url)
    authors = []
    for line in doc.select('blockquote p')[0].text.split("\n"):
        id, name = line.split(": ")
        name = re.sub('(Associate|Chief) Justice ?', '', name)
        a = opinions.Author.query.get(id)
        if not a:
            a = opinions.Author(id=id, name=name)
            opinions.db.session.add(a)
            authors.append(a)

    opinions.db.session.commit()
    return authors


def extract_urls(pdf_file):
    from StringIO import StringIO
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage

    fp = file(pdf_file, 'rb')
    laparams = LAParams()
    rsrcmgr = PDFResourceManager(caching=True)
    outtype = 'text'
    codec = 'utf-8'
    outfp = StringIO()
    pagenos = set()
    device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    for page in PDFPage.get_pages(fp, pagenos, maxpages=0, caching=True,
            check_extractable=True):
        interpreter.process_page(page)

    GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
    urls = []
    text = outfp.getvalue()

    open('text', 'w').write(text)
    text = re.sub('(http[^ ]+[^.]) +\n', r'\g<1>', text)
    text = re.sub('([^.])\n', r'\g<1>', text)
    open('text2', 'w').write(text)

    for match in GRUBER_URLINTEXT_PAT.findall(text):
        urls.append(match[0])

    return urls



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
