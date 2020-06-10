from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel, conint, conlist, constr, validator

from models.author import Author
from models.patient import Patient
from models.service import Service
from models.therapist import Therapist


class Invoice(BaseModel):
    naturapeuteID: Optional[constr(regex=r"^[a-fA-F0-9]{24}$")] = None
    author: Author
    therapist: Therapist
    patient: Patient
    servicePrice: conint(gt=0)
    services: conlist(Service, min_items=1)
    QRReference: Optional[
        constr(strip_whitespace=True, regex=r"^[0-9]{27}$")
    ] = None  # TODO : Turn into compulsory field when moving to QR-invoice
    timestamp: datetime

    # FIXME : pydantic actually does not support JavaScript negative timestamp
    #           Remove this code when it will be properly parsed.
    #           See https://github.com/samuelcolvin/pydantic/issues/1600
    @validator("timestamp", pre=True)
    @classmethod
    def check_valid_pydantic_date(cls, value):
        if value < -int(2e10):
            raise ValueError(f"Negative timestamps bigger than {2e10} are not allowed.")

        return value

    @property
    def total_amount(self) -> float:
        _total_amount: float = 0.0

        for service in self.services:
            _total_amount += service.amount(self.servicePrice / 12)

        return _total_amount

    @property
    def therapy_dates(self) -> Tuple[datetime, datetime]:
        services_dates: List[datetime] = list(service.date for service in self.services)

        return (min(services_dates), max(services_dates))