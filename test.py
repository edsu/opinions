import os
import crawl
import opinions
import tempfile
import unittest


class OpinionTests(unittest.TestCase):

    def setUp(self):
        opinions.app.config['TESTING'] = True
        self.db_fd, opinions.app.config['SQL_DATABASE_URI'] = tempfile.mkstemp()
        opinions.db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(opinions.app.config['SQL_DATABASE_URI'])

    def test_term_pages(self):
        term_pages = crawl.get_term_pages()
        self.assertTrue(len(term_pages) >= 18)
        self.assertEqual(term_pages[-1], 'http://www.supremecourt.gov/opinions/in-chambers.aspx?Term=08')


    def test_get_html_table(self):
        url = 'http://www.supremecourt.gov/opinions/slipopinions.aspx?Term=08'
        table = crawl.get_html_table(url)
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
        self.assertEqual(len(authors), 11)
        self.assertEqual(authors[0].id, "A")
        self.assertEqual(authors[0].name, "Samuel A. Alito, Jr.")

    def test_opinion(self):
        crawl.get_authors()

        url = "http://www.supremecourt.gov/opinions/slipopinions.aspx?Term=08"
        opinion_list = crawl.get_opinions(url)
        self.assertEqual(len(opinion_list), 83)
        o = opinion_list[0]
        self.assertEqual(o.name, "Ricci v. DeStefano")
        self.assertEqual(o.url, "http://www.supremecourt.gov/opinions/08pdf/07-1428.pdf")
        self.assertEqual(o.reporter_id, "83")
        self.assertEqual(o.docket_num, "07-1428")
        self.assertEqual(o.part_num, "557/2")
        self.assertEqual(o.published.year, 2009)
        self.assertEqual(o.published.month, 6)
        self.assertEqual(o.published.day, 29)
        self.assertEqual(o.author.name, "Anthony M. Kennedy")


    def test_extract(self):
        urls = crawl.extract_urls('test-data/08-1448.pdf')
        self.assertEqual(len(urls), 24)
        self.assertEqual(urls[0], 'http://www.ftc.gov/os/2009/12/P994511violententertainment.pdf')
        self.assertEqual(urls[12], 'http://ssnat.com')
        self.assertEqual(urls[23], 'http://www.youtube.com/watch?v=CFlVfVmvN6k')


if __name__ == "__main__":
    unittest.main()
