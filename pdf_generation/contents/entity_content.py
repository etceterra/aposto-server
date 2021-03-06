from typing import Union

from models import Author, Therapist


class EntityContent:
    def __init__(self, entity: Union[Author, Therapist]):
        self._entity: Union[Author, Therapist] = entity

    @property
    def gln(self) -> str:
        return "2099999999999"

    @property
    def rcc(self) -> str:
        return self._entity.rcc if self._entity.rcc else ""

    @property
    def street(self) -> str:
        return self._entity.street

    @property
    def zip_city(self) -> str:
        return f"{self._entity.zipcode} {self._entity.city}"

    @property
    def address(self) -> str:
        return f"{self.street} · {self.zip_city}"

    @property
    def phone(self) -> str:
        return self._entity.phone

    @property
    def phone_with_header(self) -> str:
        return f"Tél.  {self.phone}"
