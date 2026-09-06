#       MoMo-Flow Team

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

## Project Description

MoMo Flow is a fullstack application that ingests MoMo SMS transaction data in
XML format, cleans and normalizes it (amounts, dates, phone numbers), categorizes
transactions by type, and loads it into a relational database. A frontend
dashboard then visualizes and analyzes the processed data.

## System Architecture



## Scrum Board

[MoMo-Flow Sprint Board](https://github.com/users/nabdurahim-art/projects/1/views/1?layout_template=board)

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
