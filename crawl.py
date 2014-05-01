#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re
import sys
import time
import urllib
import logging
import datetime
import opinions
import requests
import urlparse

from bs4 import BeautifulSoup
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter


UA = "Opinions <http://github.com/edsu/opinions>"
SLEEP_BETWEEN_CRAWLS = 60 * 60 * 24 # 1 day

def crawl():
    for term_page_url in get_term_pages():
        get_opinions(term_page_url)

def get_term_pages():
    url = "http://www.supremecourt.gov/opinions/opinions.aspx"
    doc = get(url)
    urls = []
    for a in doc.select('div.dslist2 ul li a'):
        urls.append(urlparse.urljoin(url, a.get('href')))
    return urls

def get_opinions(term_page_url, parse_pdf=True):
    logging.info("fetching opinions from %s", term_page_url)
    table = get_html_table(term_page_url)
    opinion_type = get_opinion_type(term_page_url)
    opinion_list = []

    for row in table:
        # slip table has an extra first column: reporter id
        if opinion_type == "slip":
            reporter_id = row.pop(0).text
        else:
            reporter_id = None

        name = row[2].text
        pdf_url = urlparse.urljoin(term_page_url, row[2].get("href"))

        try:
            published = datetime.datetime.strptime(row[0].text, "%m/%d/%y")
        except ValueError as e:
            published = datetime.datetime.strptime(row[0].text, "%m-%d-%y")


        o = opinions.Opinion.query.filter_by(pdf_url=pdf_url).first()
        if not o:
            o = opinions.Opinion(
                type = opinion_type,
                created = datetime.datetime.now(),
                published = published,
                name = name,
                pdf_url = pdf_url,
                reporter_id = reporter_id,
                docket_num = row[1].text,
                part_num = row[4].text,
                author_id = row[3].text
            )
            opinions.db.session.add(o)
            opinions.db.session.commit()

            logging.info("found opinion: %s", o)

            if parse_pdf:
                for url in extract_urls(pdf_url):
                    e = opinions.ExternalUrl.query.filter_by(url=url, opinion=o).first()
                    if not e:
                        u = urlparse.urlparse(url)
                        e = opinions.ExternalUrl(
                            url=url, 
                            opinion=o,
                            hostname=u.netloc
                        )
                        opinions.db.session.add(e)
                        opinions.db.session.commit()
                        logging.info("found url: %s", url)

        else:
            logging.info("already have opinion: %s", o)
            
        opinion_list.append(o)

    return opinion_list

def get_html_table(url):
    doc = get(url)
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
    authors = []
    for ext in ['', '_a', '_b', '_c', '_d']:
        url = "http://www.supremecourt.gov/opinions/definitions%s.aspx" % ext
        doc = get(url)
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

def extract_urls(pdf_url):
    resp = requests.get(pdf_url, headers={"User-Agent": UA})
    fh = io.BytesIO(resp.content)
    text = get_text_from_pdf(fh)
    return get_urls_from_text(text)

def get_text_from_pdf(fh):
    laparams = LAParams()
    rsrcmgr = PDFResourceManager(caching=True)
    outtype = 'text'
    codec = 'utf-8'
    outfp = io.BytesIO()
    pagenos = set()
    device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    for page in PDFPage.get_pages(fh, pagenos, maxpages=0, caching=True,
            check_extractable=True):
        interpreter.process_page(page)

    return outfp.getvalue().decode('utf8')

def get_urls_from_text(text):
    # imperfect heuristics for massaging the text so we can get urls out 
    # in a fairly predictable manner
    text = remove_newlines(text)
    urls = re.findall('http:[^ ]+', text)
    urls = remove_weird_extensions(urls)
    urls = remove_trailing_punctuation(urls)
    return urls

def remove_newlines(text):
    # any lines that are all non-whitespace are glued on to other lines
    text = re.sub('\n([^ ]+)[\n]+', '\g<1>', text)
    # remove newlines that appear in the middle of a url
    text = re.sub(r'(http[^ \n]+)[ \n]*\n', '\g<1>', text)
    return text

def remove_trailing_punctuation(urls):
    new_urls = []
    for url in urls:
        url = re.sub('[.;,]+$', '', url)
        new_urls.append(url)
    return new_urls

def remove_weird_extensions(urls):
    """
    Turn urls like http://www.ovw.usdoj.gov/domviolence.htm.5 into
    http://www.ovw.usdoj.gov/domviolence.htm by assuming basenames with
    multiple periods are incorrect, and only the first two should be used.
    """
    new_urls = []
    for url in urls:
        u = urlparse.urlparse(url)
        path_parts = u.path.split('/')
        if u.netloc and len(path_parts) > 0:
            dotted_parts = path_parts[-1].split('.')
            path_parts[-1] = '.'.join(dotted_parts[0:2])
            new_path = '/'.join(path_parts)
            url = url.replace(u.path, new_path)
        new_urls.append(url)
    return new_urls

def get(url):
    resp = requests.get(url, headers={"User-Agent": UA})
    if resp.status_code == 200:
        return BeautifulSoup(resp.content)
    resp.raise_for_status()

def get_opinion_type(url):
    if 'slipopinions' in url:
        return 'slip'
    elif 'relatingtoorders' in url:
        return 'comment'
    elif 'in-chambers' in url:
        return 'in-chambers'
    return None

if __name__ == "__main__":
    # daemon that basically crawls, sleeps, and then crawls again ...
   
    # heroku likes log messages going to stdout
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel("INFO")

    while True:
        get_authors()
        crawl()

        logging.info("sleeping %s", SLEEP_BETWEEN_CRAWLS)
        time.sleep(SLEEP_BETWEEN_CRAWLS)
