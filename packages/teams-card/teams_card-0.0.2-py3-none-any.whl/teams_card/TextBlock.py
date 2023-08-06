from BaseElement import BaseElement


class TextBlock(BaseElement):
    SIZE_DEFAULT = "default"
    SIZE_SMALL = "small"
    SIZE_MEDIUM = "medium"
    SIZE_LARGE = "large"
    SIZE_EXTRA_LARGE = "extraLarge"

    def __init__(self) -> None:
        super().__init__()
        self._text = ""
        self._size = "default"
        self._type = "TextBlock"
        self._name = ""

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        # TODO Add validation based on specification
        self._text = text

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, text_size) -> None:
        allowed = [
            TextBlock.SIZE_DEFAULT,
            TextBlock.SIZE_SMALL,
            TextBlock.SIZE_MEDIUM,
            TextBlock.SIZE_LARGE,
            TextBlock.SIZE_EXTRA_LARGE,
        ]

        if text_size in allowed:
            self._size = text_size
        else:
            raise Exception("Text Size not allowed")

    def to_json(self) -> dict:
        return {"type": self._type, "size": self._size, "text": self._text}

    def render(self) -> str:
        d = self.to_json()
        return d.__str__()

    @staticmethod
    def make_text(text):
        # TODO Add more parameters for caller
        text_block = TextBlock()
        text_block.text = text
        return text_block
