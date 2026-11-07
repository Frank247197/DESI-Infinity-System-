import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Generate Data (Stefan-Boltzmann Law: Q = eps * sigma * A * T^4)
print("Generating radiation dataset...")
np.random.seed(42)
n_samples = 10000
epsilon = np.random.uniform(0.1, 1.0, n_samples)
area = np.random.uniform(0.1, 10.0, n_samples)
temp = np.random.uniform(300, 1000, n_samples) # Kelvin
sigma = 5.67e-8

Q = epsilon * sigma * area * (temp**4)
X = np.column_stack((epsilon, area, temp))
y = Q.reshape(-1, 1)

# 2. Split and Scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train)
y_test_scaled = scaler_y.transform(y_test)

# Convert to Tensors
X_train_t = torch.FloatTensor(X_train_scaled)
y_train_t = torch.FloatTensor(y_train_scaled)
X_test_t = torch.FloatTensor(X_test_scaled)

# 3. Define Model
class RadiationAI(nn.Module):
    def __init__(self):
        super(RadiationAI, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
    def forward(self, x):
        return self.network(x)

model = RadiationAI()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 4. Train
print("Training the Radiation AI...")
for epoch in range(1000):
    optimizer.zero_grad()
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)
    loss.backward()
    optimizer.step()
    if (epoch+1) % 200 == 0:
        print(f"Epoch {epoch+1}/1000 | Loss: {loss.item():.6f}")

# 5. Evaluate
model.eval()
with torch.no_grad():
    predictions_scaled = model(X_test_t).numpy()
    predictions = scaler_y.inverse_transform(predictions_scaled)
    actual = scaler_y.inverse_transform(y_test_scaled)

absolute_errors = np.abs(predictions - actual)
# Avoid division by zero for relative error
relative_errors = absolute_errors / np.where(actual == 0, 1e-9, actual)
max_rel_error = np.max(relative_errors) * 100

print("\n" + "="*40)
print("RADIATION AI EVALUATION RESULTS")
print("="*40)
print(f"Max Relative Error: {max_rel_error:.2f}%")

if max_rel_error < 1.0:
    print("\n✅ PASS: Radiation AI is accurate to within 1%!")
else:
    print("\n❌ FAIL: Needs tuning.")
