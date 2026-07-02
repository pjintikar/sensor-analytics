from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ────────────────────────────────────────────────────────
# 1. Device Schemas (Data gates for registering/viewing hardware)
# ────────────────────────────────────────────────────────

class DeviceCreate(BaseModel):
    """The strict blueprint of what a user MUST send to register a new device"""
    device_id: str
    device_type: str
    location: str


class DeviceResponse(BaseModel):
    """The blueprint of what our API sends back when you ask about a device"""
    id: int
    device_id: str
    device_type: str
    location: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read raw SQLAlchemy rows


# ────────────────────────────────────────────────────────
# 2. Reading Schemas (Data gates for live telemetry streams)
# ────────────────────────────────────────────────────────

class ReadingCreate(BaseModel):
    """The strict contract for incoming sensor data packets"""
    device_id: str
    temperature: float
    humidity: Optional[float] = None  # Optional means it can be left out or sent as null
    voltage: Optional[float] = None


class ReadingResponse(BaseModel):
    """The rich JSON response data sent back to the user or dashboard"""
    id: int
    device_id: str
    temperature: float
    humidity: Optional[float]
    voltage: Optional[float]
    is_anomaly: bool
    z_score: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True


# ────────────────────────────────────────────────────────
# 3. Alert Schemas (Data gates for real-time notifications)
# ────────────────────────────────────────────────────────

class AlertResponse(BaseModel):
    """The shape of data blasted out via WebSockets when an anomaly fires"""
    id: int
    device_id: str
    reading_value: float
    z_score: float
    message: str
    created_at: datetime

    class Config:
        from_attributes = True