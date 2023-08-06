"""Models for Open Data Platform of Brussel."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Garage:
    """Object representing a garage."""

    garage_id: str
    name: str
    capacity: int
    provider: str

    longitude: float
    latitude: float

    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Garage:
        """Return a Garage object from a dictionary.

        Args:
            data: The data from the API.

        Returns:
            A Garage object.
        """

        attr = data["fields"]
        geo = data["geometry"]["coordinates"]
        return cls(
            garage_id=str(data.get("recordid")),
            name=attr.get("nom_naam"),
            capacity=attr.get("nombre_de_places_aantal_plaatsen"),
            provider=attr.get("proprietaire_beheersmaatschappij"),
            longitude=geo[0],
            latitude=geo[1],
            updated_at=datetime.strptime(
                str(data.get("record_timestamp")), "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
        )


@dataclass
class DisabledParking:
    """Object representing a disabled parking."""

    spot_id: str
    number: int
    address: str

    longitude: float
    latitude: float

    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DisabledParking:
        """Return a DisabledParking object from a dictionary.

        Args:
            data: The data from the API.

        Returns:
            A DisabledParking object.
        """

        attr = data["fields"]
        geo = data["geometry"]["coordinates"]
        return cls(
            spot_id=str(data.get("recordid")),
            number=attr.get("nombre_d_emplacements"),
            address=attr.get("adres"),
            longitude=geo[0],
            latitude=geo[1],
            updated_at=datetime.strptime(
                str(data.get("record_timestamp")), "%Y-%m-%dT%H:%M:%SZ"
            ),
        )
