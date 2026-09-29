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

## Project Structure

```

.
├── api/
│   └── momo_api.py          
├── dsa/
│   ├── xml_parser.py        
│   └── search_compare.py    
├── data/
├── database/
│   └── database_setup.sql   
├── docs/
│   ├── api_docs.md                      
├── examples/
│   └── json_schemas.json    
├── tests/    
├── screenshots/             
├── etl/                     
├── web/                     
├── scripts/                 
└── README.md
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
and 

```bash
python3 -m unittest discover -s tests -v
```

## Running the DSA comparison

```bash
cd dsa
python3 xml_parser.py       
python3 search_compare.py

## Running the API

```bash
cd api
python3 momo_api.py
```

If port 8000 is already in use:

```bash
MOMO_API_PORT=8010 python3 momo_api.py
```

You should see:
```
MoMo API running on http://localhost:8000
Loaded 22 transactions from .../data/modified_sms_v2.xml
Basic Auth -> username: admin  password: momo_secret123
```

## Testing with curl

```bash
# API index — this is what http://localhost:8000/ returns after you log in
curl -u admin:momo_secret123 http://localhost:8000/

# No credentials -> 401 Unauthorized
curl -i http://localhost:8000/transactions

# List all transactions
curl -u admin:momo_secret123 http://localhost:8000/transactions

# Get one transaction
curl -u admin:momo_secret123 http://localhost:8000/transactions/1

# Create a transaction
curl -u admin:momo_secret123 -X POST -H "Content-Type: application/json" \
  -d '{"momo_ref_id":"38286099999","type":"TRANSFER","amount":1500,"sender":"Eric Manzi","receiver":"Keza Gasana","timestamp":"2026-06-01 09:00:00"}' \
  http://localhost:8000/transactions

# Update a transaction
curl -u admin:momo_secret123 -X PUT -H "Content-Type: application/json" \
  -d '{"amount":1800}' http://localhost:8000/transactions/23

# Delete a transaction
curl -u admin:momo_secret123 -X DELETE http://localhost:8000/transactions/23
```
