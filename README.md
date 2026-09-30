# Kuber.AI — Simplify Money Assignment

A Python/FastAPI backend that reproduces and extends the Kuber.AI digital-gold purchase journey.

## Features

- Natural-language conversation and intent detection
- One-time digital gold purchase
- Gold price provider with deterministic fallback
- Purchase idempotency protection
- Recurring gold SIPs
- Daily, weekly and monthly SIP scheduling
- SIP pause, resume and cancellation
- SIP installment execution
- Transaction ledger
- Decimal-based monetary calculations
- Automated tests

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest

## Project Structure

```text
app/
├── api/
│   └── routes/
├── services/
├── tests/
├── database.py
├── models.py
├── schemas.py
├── config.py
└── main.py
```

## Running the Application

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start the application

```powershell
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Running Tests

Run:

```powershell
python -m pytest -q
```

The test suite covers:

- Purchase calculation
- Four-decimal-place gold quantity rounding
- Duplicate purchase requests
- Purchase amount validation
- Gold-price fallback
- SIP scheduling
- SIP execution
- Paused and cancelled SIPs
- Conversational purchase flow
- Conversational SIP creation
- Negative purchase amounts

## Verification Flow

The complete backend flow can be demonstrated through Swagger:

1. Create a user using `POST /users`
2. Send a natural-language gold request using `POST /chat`
3. Create a one-time purchase using `POST /purchases`
4. Create a SIP using `POST /sips`
5. Execute due SIP installments using `POST /sips/execute-due`
6. Inspect purchase and ledger records
7. Check `kuber.log` for the user's financial transaction trace

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Money and Precision

Money is handled using Python `Decimal` during calculations.

Money is stored internally as integer paise, giving exact two-decimal-place rupee representation.

Gold quantity is stored internally as integer units of `0.0001` grams, giving exact four-decimal-place gold representation.

The purchase flow currently enforces:

- Minimum purchase: ₹1.00
- Maximum purchase: ₹100,000.00

Purchase quantities are calculated using deterministic decimal arithmetic and truncated to four decimal places.

## Idempotency and Duplicate Protection

Purchase requests require an idempotency key.

If the same purchase request is submitted again with the same idempotency key, the system rejects it instead of creating another purchase.

SIP creation also requires an idempotency key.

SIP installments use deterministic idempotency keys based on the SIP ID and installment due date.

This prevents retries from creating duplicate financial transactions.

## Gold Price and Dependency Failure

The gold-price service uses a primary provider abstraction and a deterministic fallback price.

If the primary provider fails or returns an invalid price, the fallback price is used.

This makes the purchase flow deterministic even when the price dependency is unavailable.

The current implementation uses a deterministic provider abstraction rather than a production external gold-price API.

## Logging and Traceability

Completed purchase events are written to:

```text
kuber.log
```

A purchase log entry contains:

- User ID
- Purchase ID
- Amount
- Gold quantity
- Gold price
- Idempotency key

Example:

```text
PURCHASE_COMPLETED | user_id=1 | purchase_id=11 | amount=₹500.00 | gold_quantity=0.0666 | gold_price=₹7500.00 | idempotency_key=purchase-demo-001
```

These fields allow the financial part of a user's journey to be reconstructed from the application logs.

## Decision Log

### 1. FastAPI

**Decision:** Use FastAPI.

**Rejected:** Flask.

**Why:** FastAPI provides request validation, automatic API documentation and a lightweight structure suitable for the assignment.

### 2. SQLite

**Decision:** Use SQLite.

**Rejected:** PostgreSQL.

**Why:** The assignment does not require deployment. SQLite keeps setup simple while still providing transactional database behaviour.

### 3. Decimal for Money

**Decision:** Use Python `Decimal` for monetary calculations.

**Rejected:** Floating-point arithmetic.

**Why:** Financial calculations require deterministic decimal arithmetic and should not rely on binary floating-point representation.

### 4. Integer Storage Units

**Decision:** Store money as paise and gold quantity as `0.0001`-gram units.

**Why:** Integer storage avoids floating-point storage errors and makes the required precision explicit.

### 5. Deterministic Gold-Price Fallback

**Decision:** Use a deterministic fallback price when the primary price provider fails.

**Why:** The assignment explicitly requires the system to survive a dependency failure.

### 6. Idempotency Keys

**Decision:** Require idempotency keys for purchases and SIP creation.

**Rejected:** Relying only on request timestamps or generated request IDs.

**Why:** Clients can retry requests. A retry must not create a second financial transaction.

### 7. Purchase Limits

**Decision:** Accept purchases from ₹1.00 to ₹100,000.00.

**Why:** This gives the system explicit handling for zero, negative, extremely small and extremely large purchase requests while keeping the validation rule simple and deterministic.

### 8. Rule-Based Intent Detection

**Decision:** Use deterministic intent detection for the core financial actions.

**Rejected:** Making every financial action dependent on an LLM.

**Why:** Financial actions need predictable behaviour. A probabilistic model should not directly determine whether a transaction is executed.

### 9. Ledger-Based Transaction History

**Decision:** Record every completed purchase and SIP installment in the ledger.

**Why:** The ledger provides an auditable transaction history and makes the user's financial activity traceable.

## AI Disclosure

AI tools were used during development for:

- Project structure suggestions
- FastAPI and SQLAlchemy implementation assistance
- Test generation
- Debugging
- Documentation drafting
- Reviewing edge cases

The generated output was manually reviewed and tested rather than being accepted without verification.

### Example of AI Output That Required Correction

During development, an initial amount parser used a regular expression that could interpret:

```text
Buy gold worth -5000
```

as the positive amount:

```text
5000
```

This was unsafe because the assignment explicitly requires sensible handling of negative purchase amounts.

The parser was changed to preserve the sign:

```python
(-?\d+(?:\.\d{1,2})?)
```

The purchase flow then rejects the resulting negative amount.

An automated test was also added for the negative purchase case.

This was an example where plausible generated/initial code required manual review against the actual assignment inputs.

## Unfinished / Known Limitations

- The current gold-price provider is represented by a deterministic provider abstraction rather than a production external gold-price API.
- Authentication and authorization are outside the scope of this assignment.
- The system uses SQLite rather than a production database.
- Docker configuration is included, but Docker was not available in the local verification environment. The application was verified using the Python/Uvicorn command.
- The conversational intent system is intentionally deterministic for financial actions.
- The current implementation is designed for the assignment scope rather than production-scale deployment.

## Docker

Docker configuration is included through:

```text
Dockerfile
docker-compose.yml
```

The intended startup command is:

```powershell
docker compose up --build
```

Docker was not available in the local environment used for development and testing, so the application was locally verified using:

```powershell
python -m uvicorn app.main:app --reload
```

## Test Result

The current test suite passes successfully.

Example:

```text
21 passed
```

Run the tests before submission:

```powershell
python -m pytest -q
```
