CREATE DATABASE IF NOT EXISTS emv_system;
USE emv_system;

SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cardholder_name VARCHAR(100) NOT NULL,
    bank VARCHAR(100) NOT NULL,
    card_type VARCHAR(20) NOT NULL,
    card_number VARCHAR(20) NOT NULL,
    expiry_date VARCHAR(10) NOT NULL,
    aid VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    UNIQUE KEY uq_cards_card_number (card_number)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    card_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transactions_card_id
        FOREIGN KEY (card_id) REFERENCES cards(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    INDEX idx_transactions_card_time (card_id, timestamp),
    INDEX idx_transactions_status (status),
    INDEX idx_transactions_risk (risk_level)
);

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    log_type VARCHAR(20) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_logs_time (timestamp),
    INDEX idx_logs_type (log_type)
);

INSERT INTO cards (cardholder_name, bank, card_type, card_number, expiry_date, aid, country, currency)
SELECT * FROM (
    SELECT 'Mohamad Fildza', 'Maybank (Simulated)', 'VISA', '4111111111111111', '12/29', 'A0000000031010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Siti Nur Aisyah', 'CIMB (Simulated)', 'MASTERCARD', '5555555555554444', '08/30', 'A0000000041010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Ahmad Firdaus', 'Bank Islam (Simulated)', 'VISA', '4000000000000028', '09/28', 'A0000000031010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Nurul Izzah', 'RHB (Simulated)', 'MASTERCARD', '5105105105105100', '11/29', 'A0000000041010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Farhan Azmi', 'Hong Leong Bank (Simulated)', 'VISA', '4012888888881881', '07/31', 'A0000000031010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Aina Syafiqah', 'AmBank (Simulated)', 'MASTERCARD', '2223003122003222', '01/30', 'A0000000041010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Zulkifli Rahman', 'Public Bank (Simulated)', 'VISA', '4111111111111234', '06/28', 'A0000000031010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Hafizah Binti Omar', 'BSN (Simulated)', 'MASTERCARD', '5200828282828210', '10/29', 'A0000000041010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Daniel Lee', 'OCBC (Simulated)', 'VISA', '4532015112830366', '05/30', 'A0000000031010', 'Malaysia', 'MYR' UNION ALL
    SELECT 'Raj Kumar', 'UOB (Simulated)', 'MASTERCARD', '5555555555551111', '03/31', 'A0000000041010', 'Malaysia', 'MYR'
) AS tmp
ON DUPLICATE KEY UPDATE
        cardholder_name = VALUES(cardholder_name),
        bank = VALUES(bank),
        card_type = VALUES(card_type),
        expiry_date = VALUES(expiry_date),
        aid = VALUES(aid),
        country = VALUES(country),
        currency = VALUES(currency);

INSERT INTO transactions (card_id, amount, status, risk_level, timestamp)
SELECT c.id, 120.50, 'APPROVED', 'LOW', NOW() - INTERVAL 20 MINUTE
FROM cards c
WHERE c.card_number = '4111111111111111'
    AND NOT EXISTS (
            SELECT 1 FROM transactions t
            WHERE t.card_id = c.id
                AND t.amount = 120.50
                AND t.status = 'APPROVED'
                AND t.risk_level = 'LOW'
    );

INSERT INTO transactions (card_id, amount, status, risk_level, timestamp)
SELECT c.id, 5500.00, 'FLAGGED', 'MEDIUM', NOW() - INTERVAL 10 MINUTE
FROM cards c
WHERE c.card_number = '5555555555554444'
    AND NOT EXISTS (
            SELECT 1 FROM transactions t
            WHERE t.card_id = c.id
                AND t.amount = 5500.00
                AND t.status = 'FLAGGED'
                AND t.risk_level = 'MEDIUM'
    );

INSERT INTO transactions (card_id, amount, status, risk_level, timestamp)
SELECT c.id, 18000.00, 'DECLINED', 'HIGH', NOW() - INTERVAL 5 MINUTE
FROM cards c
WHERE c.card_number = '4000000000000028'
    AND NOT EXISTS (
            SELECT 1 FROM transactions t
            WHERE t.card_id = c.id
                AND t.amount = 18000.00
                AND t.status = 'DECLINED'
                AND t.risk_level = 'HIGH'
    );

INSERT INTO logs (message, log_type, timestamp)
SELECT 'System initialized with Malaysian simulated EMV card data.', 'INFO', NOW() - INTERVAL 25 MINUTE
WHERE NOT EXISTS (
        SELECT 1 FROM logs
        WHERE log_type = 'INFO'
            AND message = 'System initialized with Malaysian simulated EMV card data.'
);

INSERT INTO logs (message, log_type, timestamp)
SELECT 'Seeded baseline transaction patterns for monitoring dashboard.', 'INFO', NOW() - INTERVAL 15 MINUTE
WHERE NOT EXISTS (
        SELECT 1 FROM logs
        WHERE log_type = 'INFO'
            AND message = 'Seeded baseline transaction patterns for monitoring dashboard.'
);

INSERT INTO logs (message, log_type, timestamp)
SELECT 'Anomaly simulation sample inserted for cybersecurity training.', 'ANALYSIS', NOW() - INTERVAL 8 MINUTE
WHERE NOT EXISTS (
        SELECT 1 FROM logs
        WHERE log_type = 'ANALYSIS'
            AND message = 'Anomaly simulation sample inserted for cybersecurity training.'
);

SELECT COUNT(*) AS total_cards FROM cards;
SELECT COUNT(*) AS total_transactions FROM transactions;
SELECT COUNT(*) AS total_logs FROM logs;

SELECT
        id,
        cardholder_name,
        bank,
        card_type,
        CONCAT('**** **** **** ', RIGHT(card_number, 4)) AS masked_card,
        aid,
        country,
        currency
FROM cards
ORDER BY id;

SELECT
        t.id,
        c.cardholder_name,
        c.bank,
        t.amount,
        t.status,
        t.risk_level,
        t.timestamp
FROM transactions t
JOIN cards c ON c.id = t.card_id
ORDER BY t.timestamp DESC, t.id DESC;

SELECT id, log_type, message, timestamp
FROM logs
ORDER BY timestamp DESC, id DESC;
