# ============================================================
# DESI∞ INFINITY SYSTEM - WEEK 2 EXPERIMENT
# Train a Neural Network to predict 1D Conduction Heat Transfer
# ============================================================

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Load the Data
print("Loading dataset...")
data = pd.read_csv("heat_transfer_data.csv")

# Separate inputs (X) and output (y)
X = data[["k_W_mK", "A_m2", "dT_K", "L_m"]].values
y = data[["Q_W"]].values

# 2. Split the Data (9000 Train, 1000 Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.10, random_state=42)
print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

# 3. Scale the Data (Crucial for Neural Networks to work properly)
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

y_train_scaled = scaler_y.fit_transform(y_train)
y_test_scaled = scaler_y.transform(y_test)

# Convert to PyTorch tensors
X_train_tensor = torch.FloatTensor(X_train_scaled)
y_train_tensor = torch.FloatTensor(y_train_scaled)
X_test_tensor = torch.FloatTensor(X_test_scaled)
y_test_tensor = torch.FloatTensor(y_test_scaled)

# 4. Define the Neural Network Architecture
class HeatTransferAI(nn.Module):
    def __init__(self):
        super(HeatTransferAI, self).__init__()
        # A simple network: 4 inputs -> 64 hidden neurons -> 64 hidden neurons -> 1 output
        self.network = nn.Sequential(
            nn.Linear(4, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.network(x)

model = HeatTransferAI()

# 5. Define Loss Function and Optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 6. Train the Model
print("Training the AI...")
epochs = 500
for epoch in range(epochs):
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()
    
    if (epoch+1) % 100 == 0:
        print(f"Epoch {epoch+1}/{epochs} | Loss: {loss.item():.6f}")

# 7. Evaluate on the Held-Out Test Data
model.eval()
with torch.no_grad():
    predictions_scaled = model(X_test_tensor)
    # Reverse the scaling to get actual Watts back
    predictions = scaler_y.inverse_transform(predictions_scaled.numpy())
    
# 8. Calculate Metrics (Week 3 task, built-in here for ease)
actual = y_test
absolute_errors = np.abs(predictions - actual)
relative_errors = (absolute_errors / actual) * 100

max_abs_error = np.max(absolute_errors)
max_rel_error = np.max(relative_errors)
mean_rel_error = np.mean(relative_errors)

print("\n" + "="*40)
print("AI EVALUATION RESULTS")
print("="*40)
print(f"Max Relative Error: {max_rel_error:.4f}%")
print(f"Mean Relative Error: {mean_rel_error:.4f}%")
print(f"Max Absolute Error: {max_abs_error:.4f} W")

if max_rel_error < 1.0:
    print("\n✅ PASS: The AI is accurate to within 1%!")
else:
    print("\n❌ FAIL: The AI needs more training or tuning.")
