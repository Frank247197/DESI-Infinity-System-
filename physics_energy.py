# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - NEURAL HEART MODULE
# Computational Cardiovascular Research
# ============================================================

class NeuralHeart:
    def __init__(self):
        self.name = "NEURAL_HEART"
        self.version = "6.1"

    def assess_signal_quality(self, samples, flatline_threshold=1e-5):
        if not samples or not isinstance(samples, (list, tuple)):
            raise ValueError("Samples must be a non-empty list or tuple.")
        
        # NEW: Input validation (Added here as requested by reviewer)
        if not all(isinstance(x, (int, float)) for x in samples):
            raise TypeError("All samples must be numeric.")

        min_val = min(samples)
        max_val = max(samples)
        span = max_val - min_val

        if span < flatline_threshold:
            return {
                "status": "WARNING_FLATLINE",
                "message": "Signal appears disconnected or flat.",
                "span": span
            }

        mean_val = sum(samples) / len(samples)
        return {
            "status": "VALID",
            "message": "Signal quality acceptable.",
            "mean": round(mean_val, 4),
            "min": min_val,
            "max": max_val
        }

    def estimate_heart_rate(self, peak_indices, sampling_rate_hz):
        if sampling_rate_hz <= 0:
            raise ValueError("Sampling rate must be positive.")
        if len(peak_indices) < 2:
            raise ValueError("At least two peaks are required to calculate a heart rate.")
        
        if not all(isinstance(x, int) for x in peak_indices):
            raise TypeError("Peak indices must be integers.")

        intervals_samples = []
        for i in range(len(peak_indices) - 1):
            interval = peak_indices[i+1] - peak_indices[i]
            intervals_samples.append(interval)
            
        intervals_seconds = [s / sampling_rate_hz for s in intervals_samples]
        avg_interval = sum(intervals_seconds) / len(intervals_seconds)
        bpm = 60.0 / avg_interval
        
        return {
            "bpm": round(bpm, 1),
            "avg_rr_interval_sec": round(avg_interval, 3),
            "total_beats_analyzed": len(peak_indices)
        }

    def check_heart_rate_safety(self, bpm):
        if bpm < 60:
            return {"status": "BRADYCARDIA_WARNING", "message": "Heart rate is below 60 BPM."}
        elif bpm > 100:
            return {"status": "TACHYCARDIA_WARNING", "message": "Heart rate is above 100 BPM."}
        else:
            return {"status": "NORMAL", "message": "Heart rate is within normal resting bounds."}
