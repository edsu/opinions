import os
import crawl
import logging
import opinions
import tempfile
import unittest

class OpinionTests(unittest.TestCase):

    def setUp(self):
        opinions.app.config['TESTING'] = True
        opinions.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        opinions.db.create_all()

    def test_term_pages(self):
        term_pages = crawl.get_term_pages()
        self.assertTrue(len(term_pages) >= 18)
        self.assertEqual(term_pages[-1], 'http://www.supremecourt.gov/opinions/in-chambers.aspx?Term=08')

    def test_get_html_table(self):
        pdf_url = 'http://www.supremecourt.gov/opinions/slipopinions.aspx?Term=08'
        table = crawl.get_html_table(pdf_url)
        self.assertEqual(len(table), 83)
        self.assertEqual(len(table[0]), 6)
        row = table[0]
        self.assertEqual(row[0].string, '83')
        self.assertEqual(row[1].string, '6/29/09')
        self.assertEqual(row[2].string, '07-1428')
        self.assertEqual(row[3].string, 'Ricci v. DeStefano')
        self.assertEqual(row[3].get('href'), '08pdf/07-1428.pdf')
        self.assertEqual(row[4].string, 'K')
        self.assertEqual(row[5].string, '557/2')

    def test_authors(self):
        authors = crawl.get_authors()
        self.assertEqual(len(authors), 13)
        self.assertEqual(authors[0].id, "A")
        self.assertEqual(authors[0].name, "Samuel A. Alito, Jr.")

    def test_opinion(self):
        crawl.get_authors()
        url = "http://www.supremecourt.gov/opinions/slipopinions.aspx?Term=08"
        opinion_list = crawl.get_opinions(url, parse_pdf=False)
        self.assertEqual(len(opinion_list), 83)
        o = opinion_list[0]
        self.assertEqual(o.name, "Ricci v. DeStefano")
        self.assertEqual(o.pdf_url, "http://www.supremecourt.gov/opinions/08pdf/07-1428.pdf")
        self.assertEqual(o.reporter_id, "83")
        self.assertEqual(o.docket_num, "07-1428")
        self.assertEqual(o.part_num, "557/2")
        self.assertEqual(o.published.year, 2009)
        self.assertEqual(o.published.month, 6)
        self.assertEqual(o.published.day, 29)
        self.assertEqual(o.author.name, "Anthony M. Kennedy")

    def test_extract(self):
        pdf_url = 'http://www.supremecourt.gov/opinions/10pdf/08-1448.pdf'
        urls = crawl.extract_urls(pdf_url)
        self.assertEqual(len(urls), 24)
        self.assertEqual(urls[0], 'http://www.ftc.gov/os/2009/12/P994511violententertainment.pdf')
        self.assertEqual(urls[23], 'http://www.youtube.com/watch?v=CFlVfVmvN6k')

    def test_weird_encoding(self):
        urls = crawl.extract_urls('http://www.supremecourt.gov/opinions/12pdf/11-1160_1824.pdf')
        self.assertEqual(type(urls[0]), unicode)

    def test_multiline_url(self):
        urls = crawl.get_urls_from_text('online at http://www.ovw.\n\nusdoj.gov/domviolence.htm')
        self.assertEqual(urls[0], 'http://www.ovw.usdoj.gov/domviolence.htm')

    def test_multiline_with_spaces(self):
        text = 'http://youtube.com?  \nv=123456 toodle'
        urls = crawl.get_urls_from_text(text)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], 'http://youtube.com?v=123456')

    def test_simple_url(self):
        text = 'this is an http://example.com/foo so there'
        urls = crawl.get_urls_from_text(text)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], 'http://example.com/foo')

    def test_extra_period(self):
        urls = crawl.get_urls_from_text('http://example.com/123.html.\nfoo')
        self.assertEqual(urls[0], 'http://example.com/123.html')

    def test_three_lines(self):
        urls = crawl.get_urls_from_text('http://example.com/123\n/456/789/\n012.html ')
        self.assertEqual(urls[0], 'http://example.com/123/456/789/012.html')

    def test_trailing_punctuation(self):
        urls = crawl.get_urls_from_text('http://example.com/foo.')
        self.assertEqual(urls[0], 'http://example.com/foo')
        urls = crawl.get_urls_from_text('http://example.com/foo;')
        self.assertEqual(urls[0], 'http://example.com/foo')
        urls = crawl.get_urls_from_text('http://example.com/foo,')
        self.assertEqual(urls[0], 'http://example.com/foo')

if __name__ == "__main__":
    logging.basicConfig(filename="test.log", level="INFO")
    unittest.main()
