-- 🐬 Pure MySQL Practice File
-- You can run these commands directly if you have a MySQL extension installed in your IDE.

-- 1. Create a database (if you have permissions)
CREATE DATABASE IF NOT EXISTS seo_lab;

USE seo_lab;

-- 2. Create a table
CREATE TABLE IF NOT EXISTS competitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain_name VARCHAR(255) NOT NULL,
    rank_score INT,
    last_audit DATE
);

-- 3. Insert data
INSERT INTO
    competitors (
        domain_name,
        rank_score,
        last_audit
    )
VALUES (
        'competitor1.com',
        85,
        '2024-03-14'
    ),
    (
        'competitor2.com',
        92,
        '2024-03-13'
    );

-- 4. Query

SELECT * FROM competitors WHERE rank_score > 90;