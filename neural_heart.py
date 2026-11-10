# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - NEURAL HEART MODULE
# Computational Cardiovascular Research
# ============================================================

class NeuralHeart:
    def __init__(self):
        self.name = "NEURAL_HEART"
        self.version = "6.1"

    def assess_signal_quality(self, samples, flatline_threshold=1e-5):
        """
        Evaluates the quality of a time-series signal (e.g., ECG).
        Detects flatlines (disconnected sensors) and returns basic stats.
        """
        if not samples or not isinstance(samples, (list, tuple)):
            raise ValueError("Samples must be a non-empty list or tuple.")
        
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
        """
        Estimates heart rate (BPM) from the indices of detected peaks (R-peaks).
        """
        if sampling_rate_hz <= 0:
            raise ValueError("Sampling rate must be positive.")
        if len(peak_indices) < 2:
            raise ValueError("At least two peaks are required to calculate a heart rate.")
        
        # Calculate the time intervals between peaks (RR intervals)
        intervals_samples = []
        for i in range(len(peak_indices) - 1):
            interval = peak_indices[i+1] - peak_indices[i]
            intervals_samples.append(interval)
            
        # Convert samples to seconds
        intervals_seconds = [s / sampling_rate_hz for s in intervals_samples]
        
        # Average interval
        avg_interval = sum(intervals_seconds) / len(intervals_seconds)
        
        # Calculate BPM (60 seconds / average interval)
        bpm = 60.0 / avg_interval
        
        return {
            "bpm": round(bpm, 1),
            "avg_rr_interval_sec": round(avg_interval, 3),
            "total_beats_analyzed": len(peak_indices)
        }

    def check_heart_rate_safety(self, bpm):
        """
        Checks if the heart rate falls within normal resting bounds.
        This is an educational simulation, not a medical diagnosis.
        """
        if bpm < 60:
            return {"status": "BRADYCARDIA_WARNING", "message": "Heart rate is below 60 BPM."}
        elif bpm > 100:
            return {"status": "TACHYCARDIA_WARNING", "message": "Heart rate is above 100 BPM."}
        else:
            return {"status": "NORMAL", "message": "Heart rate is within normal resting bounds."}

# ============================================================
# DEMONSTRATION
# ============================================================
if __name__ == "__main__":
    heart = NeuralHeart()
    print("="*50)
    print(f"DESI∞ {heart.name} v{heart.version} Initialized")
    print("="*50)
    
    # 1. Test Signal Quality (Synthetic ECG data)
    print("\n[1] Signal Quality Assessment:")
    # Simulating a flatline (disconnected sensor)
    flatline_signal = [0.0, 0.0, 0.0, 0.0, 0.0]
    print(f"  Flatline Test: {heart.assess_signal_quality(flatline_signal)}")
    
    # Simulating a valid signal
    valid_signal = [0.1, 0.5, 1.2, 0.4, 0.1, 0.6, 1.1, 0.3]
    print(f"  Valid Signal Test: {heart.assess_signal_quality(valid_signal)}")

    # 2. Test Heart Rate Estimation
    print("\n[2] Heart Rate Estimation:")
    # Simulating peaks detected at sample index 100, 250, 400, 550 (at 100 Hz)
    # The intervals are 150 samples (1.5 seconds) -> 40 BPM
    peak_indices = [100, 250, 400, 550]
    hr_result = heart.estimate_heart_rate(peak_indices, sampling_rate_hz=100)
    print(f"  Peaks: {peak_indices} at 100 Hz")
    print(f"  Result: {hr_result}")
    
    # 3. Test Safety Bounds
    print("\n[3] Safety Assessment:")
    print(f"  Safety Check (40 BPM): {heart.check_heart_rate_safety(40)}")
    print(f"  Safety Check (75 BPM): {heart.check_heart_rate_safety(75)}")
