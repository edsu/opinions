import os
import crawl
import opinions
import tempfile
import unittest


class OpinionTests(unittest.TestCase):

    def setUp(self):
        self.db_fd, opinions.app.config['DATABASE'] = tempfile.mkstemp()
        opinions.app.config['TESTING'] = True
        self.app = opinions.app.test_client()
        opinions.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(opinions.app.config['DATABASE'])

    def test_term_pages(self):
        term_pages = crawl.get_term_pages()
        self.assertTrue(len(term_pages) >= 18)
        self.assertEqual(term_pages[-1], 'http://www.supremecourt.gov/opinions/in-chambers.aspx?Term=08')


    def test_get_table(self):
        url = 'http://www.supremecourt.gov/opinions/slipopinions.aspx?Term=08'
        table = crawl.get_table(url)
        self.assertEqual(len(table), 84)
        self.assertEqual(len(table[0]), 6)
        
        row = table[0]
        self.assertEqual(row[0].string, 'R-')
        self.assertEqual(row[1].string, 'Date')
        self.assertEqual(row[2].string, 'Docket')
        self.assertEqual(row[3].string, 'Name')
        self.assertEqual(row[4].string, 'J.')
        self.assertEqual(row[5].string, 'Pt.')

        row = table[1]
        self.assertEqual(row[0].string, '83')
        self.assertEqual(row[1].string, '6/29/09')
        self.assertEqual(row[2].string, '07-1428')
        self.assertEqual(row[3].string, 'Ricci v. DeStefano')
        self.assertEqual(row[3].get('href'), '08pdf/07-1428.pdf')
        self.assertEqual(row[4].string, 'K')
        self.assertEqual(row[5].string, '557/2')


    def test_opinion(self):
        pass


if __name__ == "__main__":
    unittest.main()
