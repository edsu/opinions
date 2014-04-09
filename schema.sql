DROP TABLE IF EXISTS opinion;
CREATE TABLE opinion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL
);

DROP TABLE IF EXISTS author;
CREATE TABLE author (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
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
