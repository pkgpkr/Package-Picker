CREATE TABLE applications (
  id SERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  name TEXT NOT NULL,
  followers INTEGER,
  hash TEXT NOT NULL,
  retrieved TIMESTAMPTZ NOT NULL,
  CONSTRAINT unique_url UNIQUE (url)
);

CREATE TABLE packages (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  short_name TEXT,
  url TEXT,
  monthly_downloads_last_month INTEGER,
  monthly_downloads_a_year_ago INTEGER,
  absolute_trend INTEGER,
  relative_trend INTEGER,
  categories TEXT[],
  popularity INTEGER,
  bounded_popularity INTEGER,
  modified TIMESTAMPTZ,
  display_date TEXT,
  retrieved TIMESTAMPTZ NOT NULL
);

CREATE TABLE dependencies (
  application_id INTEGER REFERENCES applications (id),
  package_id INTEGER REFERENCES packages (id),
  CONSTRAINT unique_app_to_pkg UNIQUE (application_id, package_id)
);

CREATE TABLE similarity (
  package_a INTEGER REFERENCES packages (id),
  package_b INTEGER REFERENCES packages (id),
  similarity FLOAT(4) NOT NULL,
  bounded_similarity INTEGER,
  CONSTRAINT unique_pkg_to_pkg UNIQUE (package_a, package_b)
);

CREATE INDEX ON similarity (package_a);
CREATE INDEX ON similarity (package_b);
CREATE INDEX ON similarity (similarity);