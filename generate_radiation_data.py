import csv
import random

random.seed(77)

def generate_radiation_data(filename="radiation_data.csv", num_samples=10000):
    print(f"Generating {num_samples} radiation samples...")
    sigma = 5.670374419e-8  # Stefan-Boltzmann constant
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["emissivity", "A_m2", "T_hot_K", "T_cold_K", "Q_W"])
        
        for _ in range(num_samples):
            # Emissivity: 0.1 (polished metal) to 1.0 (black body)
            epsilon = round(random.uniform(0.1, 1.0), 3)
            # Area: 0.01 to 5.0 m^2
            A = round(random.uniform(0.01, 5.0), 3)
            # T_cold: Room temperature to 350K
            T_cold = round(random.uniform(250.0, 350.0), 2)
            # T_hot: Must be hotter than cold (e.g., 400K to 1500K)
            T_hot = round(random.uniform(T_cold + 50, 1500.0), 2)
            
            # Equation: Q = epsilon * sigma * A * (T_hot^4 - T_cold^4)
            Q = epsilon * sigma * A * ((T_hot**4) - (T_cold**4))
            
            writer.writerow([epsilon, A, T_hot, T_cold, round(Q, 4)])
            
    print(f"Success! Data saved to {filename}")

if __name__ == "__main__":
    generate_radiation_data()
