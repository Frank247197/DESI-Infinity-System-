import csv
import random

# Set seed for reproducibility
random.seed(101)

def generate_convection_data(filename="convection_data.csv", num_samples=10000):
    print(f"Generating {num_samples} convection samples...")
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["h_W_m2K", "A_m2", "dT_K", "Q_W"])
        
        for _ in range(num_samples):
            # h: 5 (free convection in air) to 5000 (forced convection in water)
            h = round(random.uniform(5.0, 5000.0), 3)
            # A: 0.01 to 5.0 m^2
            A = round(random.uniform(0.01, 5.0), 4)
            # dT: 1 to 300 K
            dT = round(random.uniform(1.0, 300.0), 2)
            
            # Equation: Q = h * A * dT
            Q = h * A * dT
            writer.writerow([h, A, dT, round(Q, 4)])
            
    print(f"Success! Data saved to {filename}")

if __name__ == "__main__":
    generate_convection_data()
