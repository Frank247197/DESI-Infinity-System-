import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

print("Loading radiation dataset...")
data = pd.read_csv("radiation_data.csv")

# 4 Inputs: epsilon, A, T_hot, T_cold
X = data[["emissivity", "A_m2", "T_hot_K", "T_cold_K"]].values
y = data[["Q_W"]].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.10, random_state=42)

scaler_X = StandardScaler()
scaler_y = StandardScaler()

# --- THE FIX: Log-transform the target variable BEFORE scaling ---
y_train_log = np.log1p(y_train)
y_test_log = np.log1p(y_test)

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

# Scale the log-transformed targets
y_train_scaled = scaler_y.fit_transform(y_train_log)
y_test_scaled = scaler_y.transform(y_test_log) 

X_train_tensor = torch.FloatTensor(X_train_scaled)
y_train_tensor = torch.FloatTensor(y_train_scaled)
X_test_tensor = torch.FloatTensor(X_test_scaled)

class RadiationAI(nn.Module):
    def __init__(self):
        super(RadiationAI, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(4, 128), # Increased capacity for non-linear T^4 learning
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
    def forward(self, x):
        return self.network(x)

model = RadiationAI()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.005) # Slightly lower learning rate

print("Training the Radiation AI...")
for epoch in range(1500): 
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()
    
    if (epoch+1) % 300 == 0:
        print(f"Epoch {epoch+1}/1500 | Loss: {loss.item():.6f}")

model.eval()
with torch.no_grad():
    predictions_scaled = model(X_test_tensor)
    
    # --- THE FIX: Reverse the scaling and reverse the log-transform ---
    predictions_log = scaler_y.inverse_transform(predictions_scaled.numpy())
    predictions = np.expm1(predictions_log) # This reverses np.log1p()
    
actual = y_test
absolute_errors = np.abs(predictions - actual)
relative_errors = (absolute_errors / actual) * 100

print("\n" + "="*40)
print("RADIATION AI EVALUATION RESULTS")
print("="*40)
print(f"Max Relative Error: {np.max(relative_errors):.4f}%")
print(f"Mean Relative Error: {np.mean(relative_errors):.4f}%")
print(f"Max Absolute Error: {np.max(absolute_errors):.4f} W")

if np.max(relative_errors) < 1.0:
    print("\n✅ PASS: Radiation AI is accurate to within 1%!")
else:
    print("\n❌ FAIL: Needs tuning.")
