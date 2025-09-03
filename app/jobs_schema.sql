DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company TEXT NOT NULL,
  position TEXT NOT NULL,
  applied TEXT,
  source TEXT,
  remote INTEGER,
  cover INTEGER,
  interview TEXT,
  decline TEXT,
  notes TEXT,
  UNIQUE (company, position, applied)
);
