import hashlib
import random
import time
from typing import Any, Dict


class TransactionSimulator:
    @staticmethod
    def _generate_cryptogram(prefix: str, card_number: str, amount: float) -> str:
        payload = f"{prefix}:{card_number}:{amount:.2f}:{time.time()}:{random.random()}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()
        return digest[:16]

    def simulate_transaction(self, card: Dict[str, Any], amount: float) -> Dict[str, Any]:
        arqc = self._generate_cryptogram("ARQC", card["card_number"], amount)
        arpc = self._generate_cryptogram("ARPC", card["card_number"], amount)

        status = "APPROVED"
        risk_level = "LOW"
        simulation_notes = ["Baseline profile is normal."]

        if amount <= 0:
            status = "DECLINED"
            risk_level = "HIGH"
            simulation_notes.append("Amount is invalid (<= 0).")
        elif amount >= 15000:
            status = "DECLINED"
            risk_level = "HIGH"
            simulation_notes.append("Amount exceeds high-risk threshold.")
        elif amount >= 5000:
            status = "FLAGGED"
            risk_level = "MEDIUM"
            simulation_notes.append("Amount exceeds watch threshold.")
        elif random.random() < 0.08:
            status = "FLAGGED"
            risk_level = "MEDIUM"
            simulation_notes.append("Randomized anomaly trigger fired.")

        return {
            "amount": amount,
            "arqc": arqc,
            "arpc": arpc,
            "status": status,
            "risk_level": risk_level,
            "notes": simulation_notes,
        }
