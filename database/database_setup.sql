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
