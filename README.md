#       MoMo-Flow Team
Link to task sheet: https://docs.google.com/spreadsheets/d/1jiDfgb8Cl1Nhg3a6Uj-4mDe88ngKVARnmBINzuGRuQU/edit?gid=0#gid=0


#              MoMo Flow

MoMo Flow processes MoMo SMS transaction data (XML), cleans and categorizes it,
stores it in a relational database, and presents it through a frontend dashboard
for analysis and visualization.

## Team: MoMo Flow Team

| Name | GitHub |
|------|--------|
| Nshimiyimana Abdurahim (Rahim) | [@nabdurahim-art](https://github.com/nabdurahim-art) |
| Keynes Benoit Batsinda | [@bbenoit-droid](https://github.com/bbenoit-droid) |
| Liana Batsinde (Ange Liana) | [@Ange-Liana](https://github.com/Ange-Liana) |
| Joel Mucyo | [@jmucyo-pixel](https://github.com/jmucyo-pixel) |

## Project Description

MoMo Flow is a fullstack application that ingests MoMo SMS transaction data in
XML format, cleans and normalizes it (amounts, dates, phone numbers), categorizes
transactions by type, and loads it into a relational database. A frontend
dashboard then visualizes and analyzes the processed data.

## System Architecture

See https://github.com/nabdurahim-art/momo-flow/blob/liana/architecture/Architecture.drawio.png for the high-level system architecture diagram, showing the flow from XML input through the ETL pipeline, into the database, and out to the frontend dashboard.


## Scrum Board

[MoMo-Flow Sprint Board](https://github.com/users/nabdurahim-art/projects/1/views/1?layout_template=board)

DATABASE DOCUMENTATION:

# Database

MoMo-Flow uses **MySQL 8.0+ with InnoDB** to store and process MoMo SMS/XML transaction data.

# Database Tables

The database contains five main tables:

* **`users`** — stores user and MoMo account information.
* **`categories`** — stores transaction categories such as transfers and payments.
* **`transactions`** — stores transaction details including amount, fee, balance, and date.
* **`transaction_participants`** — records users involved in a transaction and their roles (sender, receiver, agent, or merchant).
* **`system_logs`** — stores the original SMS data and its processing status.

# Relationships

* Users can have multiple transactions.
* Each transaction belongs to a user and a category.
* Transactions can have multiple participants.
* Participants are linked to both users and transactions.
* System logs can be linked to the transaction they came from.

# Data Integrity

The database uses:

* Primary and foreign keys
* Unique constraints for account numbers, category names, and MoMo reference IDs
* `NOT NULL` constraints for required fields
* `CHECK` constraints to prevent negative amounts and fees
* `ENUM` values for participant roles and processing statuses
* Indexes to improve common queries

# JSON Integration

Database records can be converted into structured JSON for API responses. Transactions can include their account owner, category, participants, and related system log information.

For more detailed information, including the ERD, data dictionary, design rationale, SQL queries, and database testing results, see the **Database Design Document**.


## Project Structure

```
.
├── README.md
├── .env.example
├── requirements.txt
├── index.html
├── api/
├── data/
├── docs/
│   └── architecture.png
├── etl/
├── scripts/
├── tests/
└── web/
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Running the ETL Pipeline

Place the provided XML export at `data/raw/momo.xml`, then:

```bash
bash scripts/run_etl.sh
```

This parses, cleans, categorizes, and loads the data into SQLite, and
exports `data/processed/dashboard.json` for the frontend.

## Running the Dashboard

```bash
bash scripts/serve_frontend.sh
```

Then open `http://localhost:8000`.

## Running Tests

```bash
pytest tests/
```
