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
        if not signal or not isinstance(signal, (list, tuple)):
            raise ValueError("Signal must be a non-empty list or tuple.")
        if not (0 < alpha <= 1):
            raise ValueError("Alpha must be between 0 and 1.")
        
        # NEW: Input validation
        if not all(isinstance(x, (int, float)) for x in signal):
            raise TypeError("All signal samples must be numeric.")

        filtered = [signal[0]]
        for i in range(1, len(signal)):
            new_val = alpha * signal[i] + (1 - alpha) * filtered[-1]
            filtered.append(new_val)
        return filtered

    def extract_time_domain_features(self, signal):
        if not signal or not isinstance(signal, (list, tuple)):
            raise ValueError("Signal must be a non-empty list or tuple.")
        
        # NEW: Input validation (Added here as requested by reviewer)
        if not all(isinstance(x, (int, float)) for x in signal):
            raise TypeError("All signal samples must be numeric.")
        
        n = len(signal)
        mean_val = sum(signal) / n
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
        features = self.extract_time_domain_features(signal)
        if features["variance"] > 1.5:
            return {"state": "ACTIVE", "confidence": "SIMULATED"}
        else:
            return {"state": "RESTING", "confidence": "SIMULATED"}

if __name__ == "__main__":
    bci = NeuroLink()
    print("="*50)
    print(f"DESI∞ {bci.name} v{bci.version} Initialized")
    print("="*50)
    
    raw_signal = [0.1, 0.8, 0.2, 1.5, 0.3, 2.0, 0.1, 1.8, 0.2, 0.9]
    print("\n[1] Raw Neural Signal:")
    print(f"  {raw_signal}")

    filtered = bci.apply_low_pass_filter(raw_signal, alpha=0.3)
    print("\n[2] Smoothed Signal (Low-Pass Filter):")
    print(f"  {[round(x, 2) for x in filtered]}")

    features = bci.extract_time_domain_features(raw_signal)
    print("\n[3] Extracted Time-Domain Features:")
    for k, v in features.items():
        print(f"  {k}: {v}")

    classification = bci.simulate_neural_state_classification(raw_signal)
    print("\n[4] Simulated BCI Classification:")
    print(f"  Predicted State: {classification['state']}")
