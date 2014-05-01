# opinions

[![Build Status](https://travis-ci.org/edsu/opinions.svg)](http://travis-ci.org/edsu/opinions)

opinions is a small Web application that watches the Supreme Court of the United States website for new [opinions](http://www.supremecourt.gov/opinions/opinions.aspx), downloads the PDFs for each decision and looks for external URLs to use as seeds for web archiving.  The [NYTimes story](http://www.nytimes.com/2013/09/24/us/politics/in-supreme-court-opinions-clicks-that-lead-nowhere.html) and [study](http://papers.ssrn.com/sol3/papers.cfm?abstract_id=2329161) brought attention to the fact that these external links are important for the interpretation of the decisions of the SCOTUS.

## Install

These instructions should get you going using sqlite as the database:

1. sudo apt-get install python python-pip virtualenvwrapper
1. mkvirtualenv opinions
1. pip install -r requirements.txt
1. python test.py
1. python opinions.py # starts the webapp on http://localhost:5000
1. python crawl.py # starts up the crawl daemon

You will see a Procfile is included for running on Heroku.

## License

* CC0
