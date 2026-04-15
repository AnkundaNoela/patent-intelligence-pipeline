-- ============================================
-- PATENT INTELLIGENCE DATABASE SCHEMA
-- ============================================

CREATE DATABASE IF NOT EXISTS patent_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE patent_db;

-- ============================================
-- TABLE 1: patents
-- ============================================
CREATE TABLE IF NOT EXISTS patents (
    patent_id       VARCHAR(20) PRIMARY KEY,
    title           MEDIUMTEXT,
    abstract        MEDIUMTEXT,
    filing_date     DATE,
    grant_date      DATE,
    year            INT,
    patent_type     VARCHAR(100),
    num_claims      INT,
    withdrawn       TINYINT(1) DEFAULT 0
);

-- ============================================
-- TABLE 2: inventors
-- ============================================
CREATE TABLE IF NOT EXISTS inventors (
    inventor_id     VARCHAR(128) PRIMARY KEY,
    first_name      VARCHAR(255),
    last_name       VARCHAR(255),
    full_name       VARCHAR(255),
    country         VARCHAR(16),
    city            VARCHAR(128),
    state           VARCHAR(20),
    latitude        FLOAT,
    longitude       FLOAT
);

-- ============================================
-- TABLE 3: companies (assignees)
-- ============================================
CREATE TABLE IF NOT EXISTS companies (
    company_id      VARCHAR(36) PRIMARY KEY,
    name            VARCHAR(256),
    assignee_type   INT(4),
    country         VARCHAR(16),
    city            VARCHAR(128)
);

-- ============================================
-- TABLE 4: patent_inventors (relationship)
-- ============================================
CREATE TABLE IF NOT EXISTS patent_inventors (
    patent_id       VARCHAR(20),
    inventor_id     VARCHAR(128),
    inventor_sequence INT,
    PRIMARY KEY (patent_id, inventor_id),
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id)
);

-- ============================================
-- TABLE 5: patent_companies (relationship)
-- ============================================
CREATE TABLE IF NOT EXISTS patent_companies (
    patent_id       VARCHAR(20),
    company_id      VARCHAR(36),
    assignee_sequence INT,
    PRIMARY KEY (patent_id, company_id),
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================
-- TABLE 6: patent_classifications (bonus)
-- ============================================
CREATE TABLE IF NOT EXISTS patent_classifications (
    patent_id       VARCHAR(20),
    cpc_section     VARCHAR(10),
    cpc_class       VARCHAR(20),
    cpc_subclass    VARCHAR(20),
    cpc_group       VARCHAR(32),
    cpc_type        VARCHAR(36),
    wipo_field_id   DOUBLE,
    wipo_sector     VARCHAR(60),
    wipo_field      VARCHAR(255),
    PRIMARY KEY (patent_id, cpc_group),
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id)
);

-- ============================================
-- INDEXES for query performance
-- ============================================
CREATE INDEX idx_patents_year ON patents(year);
CREATE INDEX idx_patents_type ON patents(patent_type);
CREATE INDEX idx_inventors_country ON inventors(country);
CREATE INDEX idx_companies_name ON companies(name(100));
CREATE INDEX idx_classifications_section ON patent_classifications(cpc_section);s