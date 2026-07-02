# Real-Time IoT Sensor Analytics & Adaptive Anomaly Detection

A high-performance, asynchronous backend data pipeline designed to ingest real-time IoT sensor telemetry metrics, execute dynamic statistical outlier evaluation, and broadcast instant incident alerts.

## 🏗️ Technical Architecture
- **API Gateway:** FastAPI & Uvicorn (Asynchronous, non-blocking network socket handling)
- **Database Engine:** PostgreSQL (ACID-compliant relational data vault)
- **Object-Relational Translator:** SQLAlchemy ORM (Optimized session pooling)
- **Mathematical Brain:** NumPy (Rolling sliding-window Z-score computation)
- **Streaming Matrix:** Full-Duplex WebSockets (Zero-latency alert broadcasting)

## 🧮 How the Analytical Brain Works
Instead of using rigid, hardcoded limits (e.g., `if temperature > 50`), this framework implements a dynamic **Z-score** algorithm. It tracks a sliding memory buffer of a device's baseline metrics, calculates the arithmetic mean ($\mu$) and standard deviation ($\sigma$), and judges new elements using:

$$Z = \frac{x - \mu}{\sigma}$$

If an incoming reading registers a Z-score greater than a strict threshold of `2.5` deviations from the norm, an anomaly state is triggered, logged to PostgreSQL, and blasted downstream via WebSockets.