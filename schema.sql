DROP TABLE IF EXISTS opinion;
CREATE TABLE opinion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created INTEGER NOT NULL,
    published INTEGER NOT NULL,
    author_id TEXT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    reporter_id TEXT,
    docket_num TEXT,
    part_num TEXT
);

DROP TABLE IF EXISTS url;
CREATE TABLE url (
    url TEXT PRIMARY KEY,
    opinion_url TEXT NOT NULL,
    created INTEGER NOT NULL,
    text TEXT
);

DROP TABLE IF EXISTS author;
CREATE TABLE author (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

/* from: http://www.supremecourt.gov/opinions/definitions.aspx */

INSERT INTO author VALUES("A", "Samuel A. Alito, Jr.");
INSERT INTO author VALUES("AS", "Antonin Scalia");
INSERT INTO author VALUES("B", "Stephen G. Breyer");
INSERT INTO author VALUES("D", "Decree in Original Case");
INSERT INTO author VALUES("DS", "David H. Souter");
INSERT INTO author VALUES("G", "Ruth Bader Ginsburg");
INSERT INTO author VALUES("JS", "John Paul Stevens");
INSERT INTO author VALUES("PC", "Unsigned Per Curiam Opinion");
INSERT INTO author VALUES("K", "Anthony M. Kennedy");
INSERT INTO author VALUES("R", "John G. Roberts, Jr.");
INSERT INTO author VALUES("T", "Clarence Thomas");
