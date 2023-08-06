"""Models for Open Data Platform of Liege."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Garage:
    """Object representing a garage."""

    name: str
    capacity: int
    charging_stations: int
    address: str
    municipality: str
    city: str
    provider: str
    schedule: str
    url: str

    longitude: float
    latitude: float

    created_at: datetime
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
            name=attr.get("title"),
            capacity=attr.get("available_spaces"),
            charging_stations=attr.get("charging_stations"),
            address=f"{attr.get('street_name')} {attr.get('house_number')}, {attr.get('postal_code')}",
            municipality=attr.get("municipality"),
            city=attr.get("city"),
            provider=attr.get("provider"),
            schedule=attr.get("schedule"),
            url=attr.get("website"),
            longitude=geo[0],
            latitude=geo[1],
            created_at=strptime(attr.get("created"), "%Y-%m-%d"),
            updated_at=strptime(attr.get("last_modified"), "%Y-%m-%d"),
        )


@dataclass
class DisabledParking:
    """Object representing a disabled parking."""

    spot_id: str
    number: int
    address: str
    municipality: str
    city: str
    status: str

    longitude: float
    latitude: float

    created_at: datetime | None
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
            number=attr.get("available_spaces"),
            address=f"{attr.get('street_name')} {attr.get('house_number')}, {attr.get('postal_code')}",
            municipality=attr.get("municipality"),
            city=attr.get("city"),
            status=attr.get("status"),
            longitude=geo[0],
            latitude=geo[1],
            created_at=strptime(attr.get("created"), "%Y-%m-%d"),
            updated_at=strptime(attr.get("last_modified"), "%Y-%m-%d"),
        )


def strptime(date_string: str, date_format: str, default: None = None) -> Any:
    """Strptime function with default value.

    Args:
        date_string: The date string.
        date_format: The format of the date string.
        default: The default value.

    Returns:
        The datetime object.
    """
    try:
        return datetime.strptime(date_string, date_format)
    except (ValueError, TypeError):
        return default
