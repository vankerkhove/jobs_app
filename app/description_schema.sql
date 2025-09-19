CREATE TABLE IF NOT EXISTS description (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER NOT NULL,
  company TEXT NOT NULL,
  position TEXT NOT NULL,
  applied TEXT,
  description TEXT,
  FOREIGN KEY (job_id) REFERENCES jobs (id)
  UNIQUE (company, position, applied)
);