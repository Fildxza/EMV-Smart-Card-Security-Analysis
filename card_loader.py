from typing import Any, Dict, List, Optional

from database import DatabaseManager


class CardLoader:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def load_cards(self) -> List[Dict[str, Any]]:
        return self.db.get_cards()

    @staticmethod
    def card_display_text(card: Dict[str, Any]) -> str:
        masked = f"**** **** **** {str(card['card_number'])[-4:]}"
        return f"{card['id']} | {card['cardholder_name']} | {card['bank']} | {masked}"

    @staticmethod
    def find_card_by_display(cards: List[Dict[str, Any]], display_text: str) -> Optional[Dict[str, Any]]:
        if not display_text:
            return None

        parts = display_text.split("|", 1)
        if not parts:
            return None

        try:
            card_id = int(parts[0].strip())
        except ValueError:
            return None

        for card in cards:
            if card.get("id") == card_id:
                return card

        return None
