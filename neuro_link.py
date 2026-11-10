# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - HEAD NEURO-LINK MODULE
# Computational Neuroscience & BCI Research
# ============================================================

import math

class NeuroLink:
    def __init__(self):
        self.name = "HEAD_NEURO-LINK"
        self.version = "6.1"

    def apply_low_pass_filter(self, signal, alpha=0.2):
        """
        Applies an Exponential Moving Average (EMA) low-pass filter.
        This smooths out high-frequency noise in neural signals.
        Alpha controls the smoothing factor (0 < alpha <= 1).
        """
        if not signal or not isinstance(signal, (list, tuple)):
            raise ValueError("Signal must be a non-empty list or tuple.")
        if not (0 < alpha <= 1):
            raise ValueError("Alpha must be between 0 and 1.")

        filtered = [signal[0]]
        for i in range(1, len(signal)):
            # EMA Formula: filtered = alpha * current + (1 - alpha) * previous
            new_val = alpha * signal[i] + (1 - alpha) * filtered[-1]
            filtered.append(new_val)
        return filtered

    def extract_time_domain_features(self, signal):
        """
        Calculates basic statistical features from a neural signal.
        Returns mean, variance, standard deviation, and peak-to-peak.
        """
        if not signal or not isinstance(signal, (list, tuple)):
            raise ValueError("Signal must be a non-empty list or tuple.")
        
        n = len(signal)
        mean_val = sum(signal) / n
        
        # Variance formula
        variance = sum((x - mean_val) ** 2 for x in signal) / n
        std_dev = math.sqrt(variance)
        
        peak_to_peak = max(signal) - min(signal)

        return {
            "mean": round(mean_val, 4),
            "variance": round(variance, 4),
            "std_dev": round(std_dev, 4),
            "peak_to_peak": round(peak_to_peak, 4)
        }

    def simulate_neural_state_classification(self, signal):
        """
        Simulates a BCI classification of a neural signal into "Resting" or "Active".
        Note: This is a simple threshold simulation, not a trained ML model.
        """
        features = self.extract_time_domain_features(signal)
        
        # If the signal variance is high, we simulate an 'Active' state
        if features["variance"] > 1.5:
            return {"state": "ACTIVE", "confidence": "SIMULATED"}
        else:
            return {"state": "RESTING", "confidence": "SIMULATED"}

# ============================================================
# DEMONSTRATION
# ============================================================
if __name__ == "__main__":
    bci = NeuroLink()
    print("="*50)
    print(f"DESI∞ {bci.name} v{bci.version} Initialized")
    print("="*50)
    
    # 1. Synthetic Neural Signal (e.g., EEG amplitudes in arbitrary units)
    raw_signal = [0.1, 0.8, 0.2, 1.5, 0.3, 2.0, 0.1, 1.8, 0.2, 0.9]

    print("\n[1] Raw Neural Signal:")
    print(f"  {raw_signal}")

    # 2. Apply Filter
    filtered = bci.apply_low_pass_filter(raw_signal, alpha=0.3)
    print("\n[2] Smoothed Signal (Low-Pass Filter):")
    print(f"  {[round(x, 2) for x in filtered]}")

    # 3. Extract Features
    features = bci.extract_time_domain_features(raw_signal)
    print("\n[3] Extracted Time-Domain Features:")
    for k, v in features.items():
        print(f"  {k}: {v}")

    # 4. Simulate Classification
    classification = bci.simulate_neural_state_classification(raw_signal)
    print("\n[4] Simulated BCI Classification:")
    print(f"  Predicted State: {classification['state']}")
    print(f"  Note: {classification['confidence']} classification.")
