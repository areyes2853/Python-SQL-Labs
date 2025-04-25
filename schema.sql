-- Drop in the correct order (employees first because it references companies)
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS companies;

-- 1. Companies table
CREATE TABLE companies (
  id            SERIAL PRIMARY KEY,
  name          VARCHAR(255) NOT NULL UNIQUE,
  industry      VARCHAR(100),
  headquarters  VARCHAR(255),
  founded_date  DATE,
  website       VARCHAR(255),
  created_at    TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at    TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- 2. Employees table
CREATE TABLE employees (
  id            SERIAL PRIMARY KEY,
  company_id    INTEGER NOT NULL
                  REFERENCES companies(id)
                  ON DELETE CASCADE,
  first_name    VARCHAR(100) NOT NULL,
  last_name     VARCHAR(100) NOT NULL,
  email         VARCHAR(255) NOT NULL UNIQUE,
  job_title     VARCHAR(100),
  hire_date     DATE,
  salary        NUMERIC(12,2),
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at    TIMESTAMP WITH TIME ZONE DEFAULT now()  -- no comma here
);

-- (Optional) index to speed up lookups by last name
CREATE INDEX idx_employees_last_name ON employees(last_name);
