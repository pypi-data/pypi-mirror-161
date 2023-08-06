import uuid

""" BaseElement.py
The base element for all components 
that can be rendered into the JSON format
"""


class BaseElement:

    def __init__(self) -> None:
        self._id = uuid.uuid1()
        self._type = "Base"

    def render(self) -> str:
        raise Exception("Base element should not be JSON rendered")

    @property
    def el_type(self):
        return self._type
