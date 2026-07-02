from collections import deque
import statistics

class AnomalyDetector:
    """
    Detects anomalies using a sliding window z-score algorithm.
    
    How it works:
    - Each device maintains its own rolling window of recent readings.
    - When a new reading arrives, we calculate how far it is from the average.
    - If it's more than `threshold` standard deviations away, it's an anomaly!
    """

    def __init__(self, window_size: int = 20, threshold: float = 2.5):
        self.window_size = window_size
        self.threshold = threshold
        # Each device gets its own private rolling deque window
        self.windows: dict[str, deque] = {}

    def check(self, device_id: str, value: float) -> tuple[bool, float | None]:
        """
        Processes a single data point.
        Returns a tuple: (is_anomaly, z_score)
        """
        # 1. Create a private window for this device if we haven't seen it before
        if device_id not in self.windows:
            self.windows[device_id] = deque(maxlen=self.window_size)

        window = self.windows[device_id]

        # 2. Gatekeeper: Need at least 10 data points before we can check for spikes
        if len(window) >= 10:
            mean = statistics.mean(window)
            stdev = statistics.stdev(window)

            if stdev > 0:  # Avoid division by zero error
                # 3. Calculate how many standard deviations away this value is
                z_score = abs(value - mean) / stdev

                if z_score > self.threshold:
                    # Anomaly detected! Do NOT add it to the window 
                    # (keeps our baseline clean from corrupt spikes)
                    return True, round(z_score, 3)

        # 4. Normal reading — add to window and drop the oldest data point
        window.append(value)
        return False, None

    def get_stats(self, device_id: str) -> dict:
        """Returns current window statistics — incredibly useful for interview demos"""
        if device_id not in self.windows or len(self.windows[device_id]) < 2:
            return {"status": "insufficient data", "count": len(self.windows.get(device_id, []))}

        window = self.windows[device_id]
        return {
            "device_id": device_id,
            "window_size": len(window),
            "mean": round(statistics.mean(window), 3),
            "stdev": round(statistics.stdev(window), 3),
            "min": round(min(window), 3),
            "max": round(max(window), 3),
        }

# Single global instance shared across the whole FastAPI application
detector = AnomalyDetector(window_size=20, threshold=2.5)