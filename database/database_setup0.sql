CREATE DATABASE IF NOT EXISTS momo_database
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
USE momo_database;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS transaction_participants;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NULL,
    account_number VARCHAR(50) NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uq_account_number UNIQUE (account_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NULL,
    CONSTRAINT pk_categories PRIMARY KEY (category_id),
    CONSTRAINT uq_category_name UNIQUE (category_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE transactions (
    transaction_id BIGINT AUTO_INCREMENT,
    momo_ref_id VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    new_balance DECIMAL(12, 2) NOT NULL,
    transaction_date DATETIME NOT NULL,
    external_tx_id VARCHAR(50) NULL,
    CONSTRAINT pk_transactions PRIMARY KEY (transaction_id),
    CONSTRAINT uq_momo_ref_id UNIQUE (momo_ref_id),
    CONSTRAINT chk_non_negative_amount CHECK (amount >= 0.00),
    CONSTRAINT chk_non_negative_fee CHECK (fee >= 0.00),
    CONSTRAINT fk_tx_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_tx_category FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE transaction_participants (
    transaction_id BIGINT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('SENDER', 'RECEIVER', 'AGENT', 'MERCHANT') NOT NULL,
    CONSTRAINT pk_tx_participants PRIMARY KEY (transaction_id, user_id, role),
    CONSTRAINT fk_part_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_part_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE system_logs (
    log_id BIGINT AUTO_INCREMENT,
    transaction_id BIGINT NULL,
    raw_sms_date BIGINT NOT NULL,
    sender_address VARCHAR(50) NOT NULL,
    message_body TEXT NOT NULL,
    status ENUM('PROCESSED', 'OTP_IGNORED', 'FAILED_PARSING', 'FAILED_VALIDATION') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_system_logs PRIMARY KEY (log_id),
    CONSTRAINT fk_logs_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Database Performance Optimizations
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date);
CREATE INDEX idx_system_logs_status ON system_logs(status);
CREATE INDEX idx_participants_user ON transaction_participants(user_id);
CREATE INDEX idx_system_logs_tx ON system_logs(transaction_id);

-- DML Test Data Seeds

INSERT INTO users (full_name, phone_number, account_number) VALUES
('Eric Manzi', '250788999000', '36521838'),
('Divine Uwase', '250791234567', '48291044'),
('Jean Paul Nshimiyimana', '250722345678', '59382011'),
('Patrick Mugisha', '250733456789', '84736251'),
('Keza Gasana', '250785678901', '29384756'),
('Inyange Retail Store', '250788000002', '00001002'),
('MTN Super Agent', '250788000001', '00001001');

INSERT INTO categories (category_name, description) VALUES
('TRANSFER', 'Peer-to-peer mobile money transfers between users'),
('BANK_DEPOSIT', 'Funds transferred directly from a bank account into a mobile wallet'),
('PAYMENT', 'Merchant or retail point-of-sale payments'),
('DATA_BUNDLE', 'Purchase of airtime, voice, or internet data packages'),
('UTILITY', 'Payments for public utilities such as electricity or water');

INSERT INTO transactions (momo_ref_id, user_id, category_id, amount, fee, new_balance, transaction_date,
external_tx_id) VALUES
('38286062599', 1, 1, 5000.00, 100.00, 45000.00, '2026-05-10 10:15:00', NULL),
('38286062600', 1, 2, 20000.00, 0.00, 65000.00, '2026-05-11 14:30:00', 'BK-8839201'),
('38286062601', 2, 3, 1200.00, 0.00, 8800.00, '2026-05-12 09:00:00', 'PAY-1002'),
('38286062602', 4, 4, 1000.00, 0.00, 14000.00, '2026-05-13 18:45:00', NULL),
('38286062603', 1, 5, 5000.00, 0.00, 40000.00, '2026-05-14 20:10:00', 'EUCL-99281');

INSERT INTO transaction_participants (transaction_id, user_id, role) VALUES
(1, 1, 'SENDER'),
(1, 2, 'RECEIVER'),
(2, 1, 'RECEIVER'),
(3, 2, 'SENDER'),
(3, 6, 'MERCHANT'),
(4, 4, 'SENDER'),
(5, 1, 'SENDER');

INSERT INTO system_logs (transaction_id, raw_sms_date, sender_address, message_body, status) VALUES
(1, 1715336100000, 'M-Money', 'TxId:38286062599 You have transferred 5,000 RWF to Divine Uwase (250791234567)
on 2026-05-10 10:15:00. New balance: 45,000 RWF.', 'PROCESSED'),
(2, 1715437800000, 'M-Money', 'TxId:38286062600 Deposit of 20,000 RWF from BK-8839201 received on 2026-05-11
14:30:00. New balance: 65,000 RWF.', 'PROCESSED'),
(3, 1715500000000, 'M-Money', 'Your Mobile Money verification OTP code is 492011. Do NOT share this code with
anyone.', 'OTP_IGNORED'),
(4, 1715600000000, 'M-Money', 'Yello! Enjoy 50% extra data on your next recharge. Dial *151# to activate today.',
'FAILED_PARSING'),
(5, 1715700000000, 'M-Money', 'TxId:38286099999 Payment failed due to insufficient wallet balance.',
'FAILED_VALIDATION');

-- Data Validation & CRUD tests

INSERT INTO users (full_name, phone_number, account_number)
VALUES ('Update Test User', '250786666666', '77567890');

SELECT * FROM users
WHERE account_number = '77567890';

UPDATE users
SET phone_number = '250787777777'
WHERE account_number = '77567890';

DELETE FROM users
WHERE account_number = '77567890';

-- Document Table Setup & Testing

SELECT
	t.transaction_id,
	t.momo_ref_id,
	t.amount,
	u.full_name AS owner_full_name,
	c.category_name,
	sl.status
FROM transactions t
JOIN users u ON t.user_id = u.user_id
JOIN categories c ON t.category_id = c.category_id LEFT
JOIN system_logs sl ON t.transaction_id = sl.transaction_id WHERE t.transaction_id = 1;

SELECT
	tp.transaction_id,
	u.full_name,
	tp.role
FROM transaction_participants tp
JOIN users u ON tp.user_id = u.user_id
WHERE tp.transaction_id = 1
ORDER BY tp.role;

-- Security & Failure testing

INSERT INTO users (full_name, phone_number, account_number)
VALUES ('Duplicate Account Test', '250700000000', '36521838');

INSERT INTO transactions (momo_ref_id, user_id, category_id, amount, fee, new_balance, transaction_date)
VALUES ('38286062599', 1, 1, 500.00, 0.00, 39500.00, '2026-05-15 10:00:00');

INSERT INTO transactions (momo_ref_id, user_id, category_id, amount, fee, new_balance, transaction_date)
VALUES ('TEST-NEGATIVE-001', 1, 1, -500.00, 0.00, 39500.00, '2026-05-15 10:00:00');

