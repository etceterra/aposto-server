from datetime import datetime
import re
from typing import List, Optional, Tuple, Union

from pydantic import BaseModel, Field, validator
from pydantic.fields import ModelField

from .author import Author
from .patient import Patient
from .service import Service
from .therapist import Therapist


class Invoice(BaseModel):
    """
    The `Invoice` model gathers all the information required for generating an invoice with Aposto,
    based on Tarif 590 and QR-invoice Swiss standards
    """

    id: Optional[str] = Field(
        None,
        title="id",
        description="The Naturapeute user ID",
        regex=r"^[a-fA-F0-9]{24}$",
    )

    author: Author = Field(
        title="Author",
        description="The invoice author. It can be the therapy society or the therapist itself",
    )

    therapist: Therapist = Field(
        title="Therapist", description="The therapist who performed the treatment"
    )

    patient: Patient = Field(
        title="Patient", description="The patient who received the treatment"
    )

    servicePrice: int = Field(
        title="Service price", description="The hourly price the therapist charges", gt=0
    )

    services: List[Service] = Field(
        title="Services",
        description="The list of services performed as part of the treatment",
        min_items=1,
        max_items=5,
    )

    timestamp: datetime = Field(
        title="Timestamp",
        description="The timestamp of the date the treatment was performed. The timestamp is expressed in milliseconds (JavaScript standard) except if negative (before 01/01/1970). If so, it is expressed in seconds",
    )

    paid: bool = Field(
        title="Paid", description="Indicates if the invoice has been paid or not"
    )

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

    @property
    def reference_type(self) -> str:
        if re.match(r"^CH[0-9]{2}3[0-1][0-9]{15}$", self.author.iban):
            return "QRR"

        return "SCOR"

    @property
    def reference(self) -> str:
        if self.reference_type == "QRR":
            return self._qr_reference

        return self._creditor_reference

    @property
    def _creditor_reference(self) -> str:
        timestamp: int = int(self.timestamp.timestamp() * 1000)

        for i in range(0, 10):
            for j in range(0, 10):
                if int(f"{timestamp}2715{i}{j}") % 97 == 1:
                    return f"RF{i}{j}{timestamp}"

    @property
    def _qr_reference(self) -> str:
        _qr_reference: str = f"{int(self.timestamp.timestamp() * 1000)}".rjust(26, "0")

        checksum_matrix = [
            [0, 9, 4, 6, 8, 2, 7, 1, 3, 5],
            [9, 4, 6, 8, 2, 7, 1, 3, 5, 0],
            [4, 6, 8, 2, 7, 1, 3, 5, 0, 9],
            [6, 8, 2, 7, 1, 3, 5, 0, 9, 4],
            [8, 2, 7, 1, 3, 5, 0, 9, 4, 6],
            [2, 7, 1, 3, 5, 0, 9, 4, 6, 8],
            [7, 1, 3, 5, 0, 9, 4, 6, 8, 2],
            [1, 3, 5, 0, 9, 4, 6, 8, 2, 7],
            [3, 5, 0, 9, 4, 6, 8, 2, 7, 1],
            [5, 0, 9, 4, 6, 8, 2, 7, 1, 3],
        ]

        checksum_key = [0, 9, 8, 7, 6, 5, 4, 3, 2, 1]

        report: int = 0

        for i in range(0, len(_qr_reference)):
            report = checksum_matrix[report][int(_qr_reference[i])]

        return f"{_qr_reference}{checksum_key[report]}"
