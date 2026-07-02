from sqlalchemy.orm import Session
from app import models, schemas

# ────────────────────────────────────────────────────────
# 1. Device Table Operations
# ────────────────────────────────────────────────────────

def create_device(db: Session, device: schemas.DeviceCreate):
    """Saves a brand-new physical device registry to the database"""
    db_device = models.Device(
        device_id=device.device_id,
        device_type=device.device_type,
        location=device.location
    )
    db.add(db_device)        # Stage the new row
    db.commit()     # Save changes permanently to the disk
    db.refresh(db_device)  # Reload to capture database-generated fields (like ID)
    return db_device


def get_device(db: Session, device_id: str):
    """Look up a specific device by its unique ID string"""
    return db.query(models.Device).filter(models.Device.device_id == device_id).first()


def get_all_devices(db: Session):
    """Retrieve an array of all registered devices in the system"""
    return db.query(models.Device).all()


# ────────────────────────────────────────────────────────
# 2. Sensor Readings Table Operations
# ────────────────────────────────────────────────────────

def create_reading(db: Session, device_id: str, temperature: float,
                   humidity: float | None, voltage: float | None,
                   is_anomaly: bool, z_score: float | None):
    """Appends a single incoming telemetry data point to the time-series log"""
    db_reading = models.SensorReading(
        device_id=device_id,
        temperature=temperature,
        humidity=humidity,
        voltage=voltage,
        is_anomaly=is_anomaly,
        z_score=z_score
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


def get_readings(db: Session, device_id: str | None = None, limit: int = 100):
    """
    Fetch historical sensor readings. 
    Optional filtering by device, ordered with newest entries first.
    """
    query = db.query(models.SensorReading)
    if device_id:
        query = query.filter(models.SensorReading.device_id == device_id)
    # Sort by timestamp descending and apply a safety cap to database load
    return query.order_by(models.SensorReading.timestamp.desc()).limit(limit).all()


def get_anomalies(db: Session, limit: int = 50):
    """Fetch the most recent flagged system anomalies exclusively"""
    return (db.query(models.SensorReading)
            .filter(models.SensorReading.is_anomaly == True)
            .order_by(models.SensorReading.timestamp.desc())
            .limit(limit)
            .all())


# ────────────────────────────────────────────────────────
# 3. Operational Alert Operations
# ────────────────────────────────────────────────────────

def create_alert(db: Session, device_id: str, reading_value: float,
                 z_score: float, message: str):
    """Log an incident entry into the dedicated alerts history table"""
    db_alert = models.Alert(
        device_id=device_id,
        reading_value=reading_value,
        z_score=z_score,
        message=message
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_alerts(db: Session, limit: int = 50):
    """Retrieve the latest operational security alerts history"""
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(limit).all()