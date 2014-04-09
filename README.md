# opinions

[![Build Status](https://travis-ci.org/edsu/opinions.svg)](http://travis-ci.org/edsu/opinions)

opinions is a small Web application that watches the Supreme Court 
of the United States website for new opinions, downloads the PDFs for each
decision and looks for external URLs to use as seeds for web archiving. 

## Install

1. sudo apt-get install python python-pip virtualenvwrapper
1. mkvirtualenv opinions
1. pip install -r requirements.txt
1. python crawl.py
1. python opinions.py

## License

* CC0
