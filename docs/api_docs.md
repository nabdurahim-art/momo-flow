# MoMo Transactions API — Documentation

Base URL: `http://localhost:8000`

All endpoints require **HTTP Basic Authentication**.

* Username: `admin`
* Password: `momo_secret123`

(Demo credentials only — see [Security Notes](#security-notes) below.)

---

## 0. GET / (API index)

Open the base URL in a browser: after the credential prompt you get this index instead of a dead end.

**Request**

```bash
curl -u admin:momo_secret123 http://localhost:8000/
```

**Response — 200 OK**

```json
{
  "name": "MoMo Transactions API",
  "endpoints": {
    "GET /transactions": "list all transactions",
    "GET /transactions/{id}": "view one transaction",
    "POST /transactions": "create a transaction",
    "PUT /transactions/{id}": "update a transaction",
    "DELETE /transactions/{id}": "delete a transaction"
  },
  "hint": "Open /transactions to see the data. Full documentation: docs/api_docs.md"
}
```

**Errors**

| Code | Meaning                                                                                         |
| ---- | ----------------------------------------------------------------------------------------------- |
| 401  | Missing or invalid Basic Auth credentials                                                       |
| 404  | Any other path (e.g. `/index.html`, `/favicon.ico`) — only `/` and `/transactions[/{id}]` exist |

---

## 1. GET /transactions

List all transactions.

**Request**

```bash
curl -u admin:momo_secret123 http://localhost:8000/transactions
```

**Response — 200 OK**

```json
{
  "count": 22,
  "transactions": [
    {
      "id": 1,
      "momo_ref_id": "38286062599",
      "type": "TRANSFER",
      "amount": 5000.0,
      "fee": 100.0,
      "new_balance": 45000.0,
      "sender": "Eric Manzi",
      "sender_phone": "250788999000",
      "receiver": "Divine Uwase",
      "receiver_phone": "250791234567",
      "timestamp": "2026-05-10 10:15:00",
      "raw_sms_date": 1715336100000,
      "status": "PROCESSED",
      "body": "TxId:38286062599 You have transferred 5,000 RWF to Divine Uwase (250791234567) on 2026-05-10 10:15:00. New balance: 45,000 RWF."
    }
  ]
}
```

**Errors**

| Code | Meaning                                   |
| ---- | ----------------------------------------- |
| 401  | Missing or invalid Basic Auth credentials |

---

## 2. GET /transactions/{id}

Fetch one transaction by id.

**Request**

```bash
curl -u admin:momo_secret123 http://localhost:8000/transactions/1
```

**Response — 200 OK**

```json
{
  "id": 1,
  "momo_ref_id": "38286062599",
  "type": "TRANSFER",
  "amount": 5000.0,
  "fee": 100.0,
  "new_balance": 45000.0,
  "sender": "Eric Manzi",
  "sender_phone": "250788999000",
  "receiver": "Divine Uwase",
  "receiver_phone": "250791234567",
  "timestamp": "2026-05-10 10:15:00",
  "raw_sms_date": 1715336100000,
  "status": "PROCESSED",
  "body": "TxId:38286062599 You have transferred 5,000 RWF to Divine Uwase (250791234567) on 2026-05-10 10:15:00. New balance: 45,000 RWF."
}
```

**Errors**

| Code | Meaning                                   |
| ---- | ----------------------------------------- |
| 400  | `id` is not a valid integer               |
| 401  | Missing or invalid Basic Auth credentials |
| 404  | No transaction with that id               |

---

## 3. POST /transactions

Create a new transaction.

**Request**

```bash
curl -u admin:momo_secret123 -X POST \
  -H "Content-Type: application/json" \
  -d '{
        "momo_ref_id": "38286099999",
        "type": "TRANSFER",
        "amount": 1500,
        "sender": "Eric Manzi",
        "receiver": "Keza Gasana",
        "timestamp": "2026-06-01 09:00:00"
      }' \
  http://localhost:8000/transactions
```

**Response — 201 Created**

```json
{
  "id": 23,
  "momo_ref_id": "38286099999",
  "type": "TRANSFER",
  "amount": 1500,
  "sender": "Eric Manzi",
  "receiver": "Keza Gasana",
  "timestamp": "2026-06-01 09:00:00"
}
```

**Errors**

| Code | Meaning                                                                                                                                                                                                                                                                      |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 400  | Malformed JSON body, body is not a JSON object (e.g. `null`, a number or an array), missing required fields (`momo_ref_id`, `type`, `amount`, `sender`, `receiver`, `timestamp`), a non-numeric `amount`/`fee`/`new_balance`, or an invalid/negative `Content-Length` header |
| 401  | Missing or invalid Basic Auth credentials                                                                                                                                                                                                                                    |
| 404  | Unknown path (anything other than `/transactions`)                                                                                                                                                                                                                           |
| 409  | Another transaction already uses this `momo_ref_id` (mirrors the unique key in `database/database_setup.sql`)                                                                                                                                                                |

---

## 4. PUT /transactions/{id}

Update an existing transaction (partial update — only send the fields you want to change).

**Request**

```bash
curl -u admin:momo_secret123 -X PUT \
  -H "Content-Type: application/json" \
  -d '{"amount": 1800, "status": "PROCESSED"}' \
  http://localhost:8000/transactions/23
```

**Response — 200 OK**

```json
{
  "id": 23,
  "momo_ref_id": "38286099999",
  "type": "TRANSFER",
  "amount": 1800,
  "sender": "Eric Manzi",
  "receiver": "Keza Gasana",
  "timestamp": "2026-06-01 09:00:00",
  "status": "PROCESSED"
}
```

**Errors**

| Code | Meaning                                                                                                                                                  |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 400  | Malformed JSON body, body is not a JSON object, invalid `id`, a non-numeric `amount`/`fee`/`new_balance`, or an invalid/negative `Content-Length` header |
| 401  | Missing or invalid Basic Auth credentials                                                                                                                |
| 404  | No transaction with that id                                                                                                                              |
| 409  | Another transaction already uses the submitted `momo_ref_id`                                                                                             |

---

## 5. DELETE /transactions/{id}

Delete a transaction.

**Request**

```bash
curl -u admin:momo_secret123 -X DELETE http://localhost:8000/transactions/23
```

**Response — 200 OK**

```json
{
  "deleted": {
    "id": 23,
    "momo_ref_id": "38286099999",
    "type": "TRANSFER",
    "amount": 1800,
    "sender": "Eric Manzi",
    "receiver": "Keza Gasana",
    "timestamp": "2026-06-01 09:00:00",
    "status": "PROCESSED"
  }
}
```

**Errors**

| Code | Meaning                                   |
| ---- | ----------------------------------------- |
| 400  | Invalid id                                |
| 401  | Missing or invalid Basic Auth credentials |
| 404  | No transaction with that id               |

---

## Error Response Format

All error responses use the same shape:

```json
{ "error": "Human-readable message" }
```

Additional notes:

* Every response — success or error — is JSON with `Content-Type: application/json`.
* `401` responses also carry `WWW-Authenticate: Basic realm="MoMo API"`.
* Malformed input is answered with `400`; the server does not drop the connection on bad JSON, a non-object body, or an invalid `Content-Length` header.

## Security Notes

**Why Basic Auth is weak:**

* Credentials are only base64-encoded, not encrypted — anyone who intercepts the request (e.g. on an unsecured network) can trivially decode the username and password.
* The exact same credentials are sent on *every single request*, so there's no session expiry — a captured header works forever until the password is changed.
* There's no way to scope access (e.g. read-only vs admin) or revoke a single client without changing the shared password for everyone.
* It doesn't support multi-factor auth or delegated/third-party access.

**Stronger alternatives:**

* **JWT (JSON Web Tokens):** the server issues a signed, short-lived token after login; the client sends the token instead of raw credentials on each request, and the token can encode expiry, scopes, and user identity without a database lookup.
* **OAuth 2.0:** standardizes delegated authorization (e.g. "let this app access my MoMo data without giving it my password"), supports token refresh, scoped permissions, and revocation, and is the standard for third-party mobile/web app integrations.
* In production, Basic Auth should also always run over HTTPS/TLS at a minimum, regardless of which auth scheme is used.
