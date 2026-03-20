from typing import Any, Dict, List

from database import DatabaseManager


class SecurityAnalyzer:
    VALID_AIDS = {
        "VISA": "A0000000031010",
        "MASTERCARD": "A0000000041010",
    }

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def analyze(self, card: Dict[str, Any], transaction: Dict[str, Any]) -> Dict[str, Any]:
        findings: List[str] = []
        score = 0

        required_card_fields = [
            "cardholder_name",
            "bank",
            "card_type",
            "card_number",
            "expiry_date",
            "aid",
            "country",
            "currency",
        ]
        missing = [field for field in required_card_fields if not card.get(field)]
        if missing:
            score += 3
            findings.append(f"Missing card fields: {', '.join(missing)}")

        expected_aid = self.VALID_AIDS.get(card.get("card_type", "").upper())
        if not expected_aid:
            score += 2
            findings.append("Unknown card type for AID validation.")
        elif card.get("aid") != expected_aid:
            score += 3
            findings.append("Card AID mismatch detected.")

        amount = float(transaction.get("amount", 0))
        if amount <= 0:
            score += 4
            findings.append("Invalid amount value.")
        elif amount >= 10000:
            score += 4
            findings.append("Very high transaction amount.")
        elif amount >= 3000:
            score += 2
            findings.append("Unusually high transaction amount.")

        recent_tx = self.db.get_recent_transactions(card_id=card["id"], minutes=3, limit=10)
        if len(recent_tx) >= 3:
            score += 2
            findings.append("High frequency transactions in a short window.")

        if transaction.get("status") == "DECLINED":
            score += 2
            findings.append("Simulator already marked transaction as DECLINED.")
        elif transaction.get("status") == "FLAGGED":
            score += 1
            findings.append("Simulator flagged this transaction.")

        if score >= 6:
            risk_level = "HIGH"
            status = "DECLINED"
        elif score >= 3:
            risk_level = "MEDIUM"
            status = "FLAGGED"
        else:
            risk_level = "LOW"
            status = "APPROVED"
            findings.append("No significant anomaly indicators found.")

        return {
            "risk_level": risk_level,
            "status": status,
            "score": score,
            "findings": findings,
        }
