# EMV Smart Card Security Analysis and Transaction Monitoring System

Educational cybersecurity simulation project using Malaysian-style EMV card dummy data with MySQL persistence.

## Disclaimer
This project is strictly for educational and cybersecurity research use only.
All card details are simulated test data.
No real banking APIs, no real customer data, and no live financial integrations are used.

## Tech Stack
- Python 3
- MySQL
- Tkinter desktop UI
- mysql-connector-python
- matplotlib

## Project Structure
- `database.py` - MySQL setup, table creation, dummy seeding, transaction/log persistence
- `card_loader.py` - Card retrieval and dropdown display formatting
- `transaction_simulator.py` - Simulated ARQC/ARPC generation and transaction behavior
- `security_analyzer.py` - AID checks, anomaly scoring, and risk classification
- `dashboard.py` - Main desktop dashboard UI (left/center/right/bottom layout)
- `app.py` - Simple entrypoint
- `init_db.sql` - SQL schema + dummy insertion script

## Database
Default database name: `emv_system`

Tables:
- `cards`
- `transactions`
- `logs`

The app auto-creates the database and tables, then seeds 10 Malaysian dummy card records if `cards` is empty.

## Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure MySQL server is running.
3. Configure DB access via environment variables if needed:
   - `EMV_DB_HOST` (default: `localhost`)
   - `EMV_DB_PORT` (default: `3306`)
   - `EMV_DB_USER` (default: `root`)
   - `EMV_DB_PASSWORD` (default: empty)

## Run
```bash
python app.py
```

## Feature Mapping
- Card Loader:
  - Loads cards from MySQL into dropdown
- Transaction Simulator:
  - Amount input
  - Simulated ARQC/ARPC generation
- Security Analyzer:
  - Missing data check
  - AID validation
  - Anomaly scoring and risk level assignment (`LOW`, `MEDIUM`, `HIGH`)
- Dashboard:
  - Left panel: Card Info
  - Center panel: Transaction Simulation and control buttons
  - Right panel: Security Analysis findings, risk indicator, and built-in graphs
  - Bottom panel: Logs timeline
- Logging:
  - Every major event is written to `logs`
  - Final analysis outcome saved to `transactions`
- CSV Export:
  - One-click export of logs to CSV from dashboard
- Visualization:
  - Risk trend chart from recent transactions
  - Status distribution chart (`APPROVED`/`FLAGGED`/`DECLINED`)
- Theme Switching:
  - Runtime dark mode and light mode toggle

## Risk Output
- Normal:
  - Status: `APPROVED`
  - Risk: `LOW`
- Suspicious:
  - Status: `FLAGGED`
  - Risk: `MEDIUM`
- High Risk:
  - Status: `DECLINED`
  - Risk: `HIGH`
