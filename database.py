import os
from typing import Any, Dict, List, Optional

import mysql.connector
from mysql.connector import Error


DB_NAME = "emv_system"


class DatabaseManager:
    def __init__(self) -> None:
        self.host = os.getenv("EMV_DB_HOST", "localhost")
        self.user = os.getenv("EMV_DB_USER", "root")
        self.password = os.getenv("EMV_DB_PASSWORD", "")
        self.port = int(os.getenv("EMV_DB_PORT", "3306"))
        self.connection_timeout = int(os.getenv("EMV_DB_CONNECT_TIMEOUT", "5"))

    def _get_server_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            connection_timeout=self.connection_timeout,
            use_pure=True,
            autocommit=True,
        )

    def _get_db_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            database=DB_NAME,
            connection_timeout=self.connection_timeout,
            use_pure=True,
            autocommit=True,
        )

    def initialize_database(self) -> None:
        server_conn = None
        db_conn = None
        try:
            server_conn = self._get_server_connection()
            with server_conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

            db_conn = self._get_db_connection()
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cards (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        cardholder_name VARCHAR(100),
                        bank VARCHAR(100),
                        card_type VARCHAR(20),
                        card_number VARCHAR(20),
                        expiry_date VARCHAR(10),
                        aid VARCHAR(50),
                        country VARCHAR(50),
                        currency VARCHAR(10)
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        card_id INT,
                        amount DECIMAL(10, 2),
                        status VARCHAR(20),
                        risk_level VARCHAR(20),
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (card_id) REFERENCES cards(id)
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        message TEXT,
                        log_type VARCHAR(20),
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        except Error as error:
            raise RuntimeError(f"Database initialization failed: {error}") from error
        finally:
            if db_conn and db_conn.is_connected():
                db_conn.close()
            if server_conn and server_conn.is_connected():
                server_conn.close()

    def seed_dummy_cards(self) -> None:
        cards = [
            {
                "cardholder_name": "Mohamad Fildza",
                "bank": "Maybank (Simulated)",
                "card_type": "VISA",
                "card_number": "4111111111111111",
                "expiry_date": "12/29",
            },
            {
                "cardholder_name": "Siti Nur Aisyah",
                "bank": "CIMB (Simulated)",
                "card_type": "MASTERCARD",
                "card_number": "5555555555554444",
                "expiry_date": "08/30",
            },
            {
                "cardholder_name": "Ahmad Firdaus",
                "bank": "Bank Islam (Simulated)",
                "card_type": "VISA",
                "card_number": "4000000000000028",
                "expiry_date": "09/28",
            },
            {
                "cardholder_name": "Nurul Izzah",
                "bank": "RHB (Simulated)",
                "card_type": "MASTERCARD",
                "card_number": "5105105105105100",
                "expiry_date": "11/29",
            },
            {
                "cardholder_name": "Farhan Azmi",
                "bank": "Hong Leong Bank (Simulated)",
                "card_type": "VISA",
                "card_number": "4012888888881881",
                "expiry_date": "07/31",
            },
            {
                "cardholder_name": "Aina Syafiqah",
                "bank": "AmBank (Simulated)",
                "card_type": "MASTERCARD",
                "card_number": "2223003122003222",
                "expiry_date": "01/30",
            },
            {
                "cardholder_name": "Zulkifli Rahman",
                "bank": "Public Bank (Simulated)",
                "card_type": "VISA",
                "card_number": "4111111111111234",
                "expiry_date": "06/28",
            },
            {
                "cardholder_name": "Hafizah Binti Omar",
                "bank": "BSN (Simulated)",
                "card_type": "MASTERCARD",
                "card_number": "5200828282828210",
                "expiry_date": "10/29",
            },
            {
                "cardholder_name": "Daniel Lee",
                "bank": "OCBC (Simulated)",
                "card_type": "VISA",
                "card_number": "4532015112830366",
                "expiry_date": "05/30",
            },
            {
                "cardholder_name": "Raj Kumar",
                "bank": "UOB (Simulated)",
                "card_type": "MASTERCARD",
                "card_number": "5555555555551111",
                "expiry_date": "03/31",
            },
        ]

        conn = None
        try:
            conn = self._get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM cards")
                row = cursor.fetchone()
                if row and row["total"] > 0:
                    return

                insert_sql = (
                    "INSERT INTO cards "
                    "(cardholder_name, bank, card_type, card_number, expiry_date, aid, country, currency) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                )

                for card in cards:
                    aid = "A0000000031010" if card["card_type"] == "VISA" else "A0000000041010"
                    cursor.execute(
                        insert_sql,
                        (
                            card["cardholder_name"],
                            card["bank"],
                            card["card_type"],
                            card["card_number"],
                            card["expiry_date"],
                            aid,
                            "Malaysia",
                            "MYR",
                        ),
                    )
        except Error as error:
            raise RuntimeError(f"Failed to seed cards: {error}") from error
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_cards(self) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM cards ORDER BY id ASC")
                return cursor.fetchall()
        except Error as error:
            raise RuntimeError(f"Failed to load cards: {error}") from error
        finally:
            if conn and conn.is_connected():
                conn.close()

    def save_transaction(self, card_id: int, amount: float, status: str, risk_level: str) -> None:
        conn = None
        try:
            conn = self._get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO transactions (card_id, amount, status, risk_level) VALUES (%s, %s, %s, %s)",
                    (card_id, amount, status, risk_level),
                )
        except Error as error:
            raise RuntimeError(f"Failed to save transaction: {error}") from error
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_recent_transactions(self, card_id: int, minutes: int = 5, limit: int = 10) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id, amount, status, risk_level, timestamp
                    FROM transactions
                    WHERE card_id = %s
                    AND timestamp >= (NOW() - INTERVAL %s MINUTE)
                    ORDER BY timestamp DESC
                    LIMIT %s
                    """,
                    (card_id, minutes, limit),
                )
                return cursor.fetchall()
        except Error as error:
            raise RuntimeError(f"Failed to fetch recent transactions: {error}") from error
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_transactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id, card_id, amount, status, risk_level, timestamp
                    FROM transactions
                    ORDER BY timestamp DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                return cursor.fetchall()
        except Error as error:
            raise RuntimeError(f"Failed to fetch transactions: {error}") from error
        finally:
            if conn and conn.is_connected():
                conn.close()

    def save_log(self, message: str, log_type: str) -> None:
        conn = None
        try:
            conn = self._get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO logs (message, log_type) VALUES (%s, %s)",
                    (message, log_type),
                )
        except Error as error:
            raise RuntimeError(f"Failed to save log: {error}") from error
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_logs(self, limit: int = 200) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT id, message, log_type, timestamp FROM logs ORDER BY id DESC LIMIT %s",
                    (limit,),
                )
                return cursor.fetchall()
        except Error as error:
            raise RuntimeError(f"Failed to fetch logs: {error}") from error
        finally:
            if conn and conn.is_connected():
                conn.close()
