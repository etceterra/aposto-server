from datetime import datetime

from pydantic import BaseModel, Field
from typing_extensions import Literal


class Service(BaseModel):
    """
    A service performed. It corresponds to a therapy and its duration
    """

    date: datetime = Field(
        title="Date",
        description="The timestamp of the date the therapy was performed. The timestamp is expressed in milliseconds (JavaScript standard) except if negative (before 01/01/1970). If so, it is expressed in seconds",
    )

    duration: int = Field(
        title="Duration", description="The therapy duration", ge=5, multiple_of=5
    )

    code: Literal[
        1003,
        1004,
        1005,
        1006,
        1008,
        1010,
        1012,
        1013,
        1014,
        1017,
        1021,
        1022,
        1024,
        1025,
        1026,
        1027,
        1028,
        1029,
        1030,
        1032,
        1033,
        1034,
        1039,
        1045,
        1047,
        1048,
        1049,
        1050,
        1051,
        1052,
        1054,
        1055,
        1056,
        1057,
        1058,
        1060,
        1061,
        1062,
        1063,
        1064,
        1065,
        1066,
        1067,
        1068,
        1069,
        1070,
        1071,
        1072,
        1076,
        1077,
        1079,
        1080,
        1081,
        1082,
        1084,
        1085,
        1087,
        1088,
        1089,
        1091,
        1092,
        1093,
        1094,
        1096,
        1097,
        1098,
        1100,
        1102,
        1104,
        1105,
        1106,
        1111,
        1114,
        1115,
        1117,
        1120,
        1121,
        1122,
        1123,
        1131,
        1132,
        1134,
        1140,
        1141,
        1142,
        1200,
        1202,
        1203,
        1204,
        1205,
        1206,
        1207,
        1210,
    ] = Field(
        title="Code", description="The therapy code as defined in the Tarif 590 standard"
    )

    @property
    def quantity(self) -> float:
        return self.duration / 5

    def amount(self, service_unit_price) -> float:
        return service_unit_price * self.quantity
