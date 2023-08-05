from typing import Optional, Dict, List
from datetime import datetime
from pydantic.dataclasses import dataclass


@dataclass
class Ais:
    MMSI: int
    BaseDateTime: datetime
    LAT: float
    LON: float
    SOG: Optional[float]
    COG: Optional[float]
    Heading: Optional[float]
    VesselName: Optional[str]
    IMO: Optional[str]
    CallSign: Optional[str]
    VesselType: Optional[str]
    Status: Optional[str]
    Length: Optional[str]
    Width: Optional[str]
    Draft: Optional[str]
    Cargo: Optional[str]
    TranscieverClass: Optional[str]
    location: Optional[List]


@dataclass
class Track:
    coordinates: list
    MMSI: str
    TrackStartTime: datetime
    TrackEndTime: datetime
    Distance: float
    Speed: float
    vessel: Optional[Ais]
