from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional

from app.database import engine, get_db
from app import models, schemas, crud
from app.anomaly import detector
from app.websocket_manager import manager

# 1. Automatic Database Table Generation
models.Base.metadata.create_all(bind=engine)

# 2. Initialize the FastAPI Core Engine
app = FastAPI(
    title="IoT Sensor Analytics API",
    description="Real-time sensor monitoring with automated anomaly detection",
    version="1.0.0"
)


# ────────────────────────────────────────────────────────
# Health Check Gateway
# ────────────────────────────────────────────────────────
@app.get("/")
def health_check():
    """Simple confirmation that the server is online and listening"""
    return {"status": "online", "message": "Sensor Analytics API is running"}


# ────────────────────────────────────────────────────────
# Device Inventory Gateways
# ────────────────────────────────────────────────────────
@app.post("/devices", response_model=schemas.DeviceResponse, status_code=201)
def register_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    """Registers a new IoT device registry into our ecosystem"""
    existing = crud.get_device(db, device.device_id)
    if existing:
        raise HTTPException(status_code=400, detail="Device already registered")
    return crud.create_device(db, device)


@app.get("/devices", response_model=list[schemas.DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    """Fetches an inventory checklist of all registered edge components"""
    return crud.get_all_devices(db)


@app.get("/devices/{device_id}", response_model=schemas.DeviceResponse)
def get_device(device_id: str, db: Session = Depends(get_db)):
    """Looks up information on an individual hardware component by its unique ID"""
    device = crud.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


# ────────────────────────────────────────────────────────
# The Core Telemetry Ingestion Pipeline (The Crown Jewel)
# ────────────────────────────────────────────────────────
@app.post("/readings", response_model=schemas.ReadingResponse, status_code=201)
async def ingest_reading(reading: schemas.ReadingCreate, db: Session = Depends(get_db)):
    """
    Main Data Highway. Receives high-velocity real-time sensor metrics:
    1. Feeds metric to the adaptive statistical Z-score engine.
    2. Writes telemetry records securely into PostgreSQL.
    3. If marked an anomaly, builds a high-priority incident alert 
       and blasts it down the live WebSocket streaming channels instantly.
    """
    # Step 1: Run streaming metric against our Z-score sliding windows
    is_anomaly, z_score = detector.check(reading.device_id, reading.temperature)

    # Step 2: Persist the telemetry entry to the physical database logs
    db_reading = crud.create_reading(
        db=db,
        device_id=reading.device_id,
        temperature=reading.temperature,
        humidity=reading.humidity,
        voltage=reading.voltage,
        is_anomaly=is_anomaly,
        z_score=z_score
    )

    # Step 3: Trigger real-time defensive broadcast sequences if a spike is confirmed
    if is_anomaly:
        # Enforce a safe fallback to 0.0 to satisfy the strict Pylance static type checker
        safe_z_score = z_score if z_score is not None else 0.0
        
        message = f"Anomaly on {reading.device_id}: temp={reading.temperature}°C (z={safe_z_score})"
        
        # Log incident data into PostgreSQL table logs for audit history
        crud.create_alert(db, reading.device_id, reading.temperature, safe_z_score, message)

        # Blast JSON network packets to all listening terminal dashboard browsers
        await manager.broadcast_alert({
            "type": "anomaly",
            "device_id": reading.device_id,
            "temperature": reading.temperature,
            "z_score": safe_z_score,
            "message": message
        })

    return db_reading


@app.get("/readings", response_model=list[schemas.ReadingResponse])
def get_readings(device_id: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves standard telemetry histories, with optional device-specific filters"""
    return crud.get_readings(db, device_id=device_id, limit=limit)


@app.get("/readings/anomalies", response_model=list[schemas.ReadingResponse])
def get_anomalies(db: Session = Depends(get_db)):
    """Exclusively extracts flagged anomaly streams from database logs"""
    return crud.get_anomalies(db)


# ────────────────────────────────────────────────────────
# Operational Alert Ledger
# ────────────────────────────────────────────────────────
@app.get("/alerts", response_model=list[schemas.AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    """Retrieves full incident logs history for operators to evaluate"""
    return crud.get_alerts(db)


# ────────────────────────────────────────────────────────
# Debugging Analytics Statistics Endpoint
# ────────────────────────────────────────────────────────
@app.get("/stats/{device_id}")
def get_device_stats(device_id: str):
    """Exposes memory statistics window parameters to evaluate baseline values"""
    return detector.get_stats(device_id)


# ────────────────────────────────────────────────────────
# Persistent Real-Time Live Stream Pipeline (WebSockets)
# ────────────────────────────────────────────────────────
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    Persistent system pipeline interface dashboard interface. Keeps a steady 
    live-stream connection path open to instantly display active alerts.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keeps connection highway alive by monitoring ping-pong heartbeats
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Gracefully handle unexpected connection severing (e.g., closing browser tab)
        manager.disconnect(websocket)