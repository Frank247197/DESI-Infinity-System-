import csv
import random

def generate_dataset(filename="heat_transfer_data.csv", num_samples=100):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["k_W_mK", "A_m2", "dT_K", "L_m", "Q_W"])
        
        for _ in range(num_samples):
            k = round(random.uniform(0.5, 400.0), 2)   # Material conductivity
            A = round(random.uniform(0.1, 5.0), 2)     # Area
            dT = round(random.uniform(10.0, 100.0), 2) # Temp difference
            L = round(random.uniform(0.01, 1.0), 2)    # Thickness
            
            Q = (k * A * dT) / L
            writer.writerow([k, A, dT, L, round(Q, 2)])

    print(f"Dataset generated: {filename}")

if __name__ == "__main__":
    generate_dataset()
