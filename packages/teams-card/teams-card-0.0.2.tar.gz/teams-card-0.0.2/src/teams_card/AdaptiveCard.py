from typing import List

from src.teams_card.BaseElement import BaseElement


class AdaptiveCard:
    card_schema = "http://adaptivecards.io/schemas/adaptive-card.json"
    card_version = "1.0"

    def __init__(self) -> None:
        self._body_items = []

    def add_element(self, element: BaseElement) -> None:
        self._body_items.append(element)

    def to_json(self):
        # Combine all the Rendered elements
        body_render = ",".join([i.render() for i in self._body_items])

        d = {"$schema": AdaptiveCard.card_schema,
             "type": "AdaptiveCard",
             "version": self.card_version,
             "body": body_render}
        return d

    def render(self) -> str:
        d = self.to_json()
        return d.__str__()
