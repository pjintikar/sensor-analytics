from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# 1. The Device Table Model
class Device(Base):
    """Represents one physical sensor device (like an ESP32 microcontroller)"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)   # e.g., "ESP32_001"
    device_type = Column(String)                           # e.g., "temperature"
    location = Column(String)                              # e.g., "Server Room"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Establishes a link in Python to look up readings easily
    readings = relationship("SensorReading", back_populates="device")


# 2. The Sensor Readings Table Model
class SensorReading(Base):
    """Stores every incoming telemetry data point sent by the devices"""
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    temperature = Column(Float)
    humidity = Column(Float, nullable=True)  # nullable=True means this can be left blank
    voltage = Column(Float, nullable=True)
    is_anomaly = Column(Boolean, default=False)   # Flagged True if our Z-score math says it's a spike
    z_score = Column(Float, nullable=True)         # Stores how many standard deviations away it was
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Links this reading back to its parent device row
    device = relationship("Device", back_populates="readings")


# 3. The Alerts Table Model
class Alert(Base):
    """A dedicated log for security/maintenance alerts when an anomaly triggers"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String)
    reading_value = Column(Float)
    z_score = Column(Float)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)