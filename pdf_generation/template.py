import json
from abc import ABC
from pathlib import Path
from typing import List

from .content import Content, Graphic, SwissQRCode, Text, Value


class Template(ABC):
    def __init__(self, path: Path):
        self.path: Path = path
        self.load_template()

    def load_template(self) -> List[Content]:
        pass


class DescriptorTemplate(Template):
    def load_template(self) -> List[Text]:
        with open(self.path.resolve().as_posix()) as json_template:
            return list(Text(dict_text) for dict_text in json.load(json_template))


class GraphicTemplate(Template):
    def load_template(self) -> List[Graphic]:
        with open(self.path.resolve().as_posix()) as json_template:
            return list(
                Graphic(dict_graphic) for dict_graphic in json.load(json_template)
            )


class ValueTemplate(Template):
    def load_template(self):
        with open(self.path.resolve().as_posix()) as json_template:
            return list(Value(dict_value) for dict_value in json.load(json_template))


class SwissQRCodeTemplate(Template):
    def load_template(self) -> List[SwissQRCode]:
        with open(self.path.resolve().as_posix()) as json_template:
            return list(
                SwissQRCode(dict_swiss_qr_code)
                for dict_swiss_qr_code in json.load(json_template)
            )
