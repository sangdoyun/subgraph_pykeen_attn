"""
| Activity Type            | Description                                             | Temporal Pattern                     |
| ------------------------ | ------------------------------------------------------- | ------------------------------------ |
| **Morning Walk**         | Regular, 6–7AM photos / GPS / steps                     | Clustered burst in early morning     |
| **Cooking Session**      | Multiple small events (10–20 mins) from 11AM–1PM, 6–8PM | Two bursts, mid-day + evening        |
| **Family Event (short)** | Few face/photos around 4–6PM                            | Dense but short burst in evening     |
| **Full-Day Travel**      | Scattered images from 8AM–10PM, with location drift     | High entropy, high span, low density |
| **Running (exercise)**   | Tight burst of photos + steps at 6–6:45AM               | One dense block, short duration      |
| **Routine Work Day**     | Low activity, few events between 10AM–6PM               | Low entropy, middle of day           |
"""

# Install required packages if needed:
# pip install numpy matplotlib scikit-learn torch

import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Synthetic data generation
def generate_activity_data():
    activities = {
        "morning_walk": lambda: np.random.normal(loc=360, scale=10, size=np.random.randint(10, 20)),
        "cooking_session": lambda: np.concatenate([
            np.random.normal(loc=720, scale=15, size=np.random.randint(5, 10)),
            np.random.normal(loc=1140, scale=15, size=np.random.randint(5, 10))
        ]),
        "family_event_short": lambda: np.random.normal(loc=1020, scale=20, size=np.random.randint(10, 20)),
        "full_day_travel": lambda: np.random.uniform(480, 1320, size=np.random.randint(20, 40)),
        "running": lambda: np.random.normal(loc=390, scale=5, size=np.random.randint(10, 15)),
        "routine_work_day": lambda: np.random.uniform(600, 1080, size=np.random.randint(5, 10)),
    }

    label_to_idx = {k: i for i, k in enumerate(activities)}
    data = []

    for label, gen in activities.items():
        for _ in range(500):
            ts = gen()
            ts = np.clip(ts, 0, 1439)
            ts = sorted(ts)
            norm_ts = [t / 1440.0 for t in ts]
            data.append((norm_ts, label_to_idx[label]))

    return data, label_to_idx

# Dataset
class TimeDataset(Dataset):
    def __init__(self, data, max_len=50):
        self.data = data
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        x, y = self.data[idx]
        x_arr = np.zeros(self.max_len)
        x_arr[:min(len(x), self.max_len)] = x[:self.max_len]
        return torch.tensor(x_arr, dtype=torch.float32), y

# Model
class TemporalEncoder(nn.Module):
    def __init__(self, emb_dim=16):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(32, emb_dim)

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.conv(x)
        x = self.pool(x).squeeze(-1)
        return self.fc(x)

# Train function (fixed)
def train_unsup_model(data, emb_dim=16, epochs=20):
    dataset = TimeDataset(data)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    model = TemporalEncoder(emb_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    # Ensure float32 data
    raw_ts = [d[0] + [0]*(50 - len(d[0])) for d in data]
    raw_ts_np = np.array(raw_ts, dtype=np.float32)

    # Self-supervised: Use KMeans to assign pseudo-labels
    km = KMeans(n_clusters=6, random_state=0).fit(raw_ts_np)
    centers = torch.tensor(km.cluster_centers_[:, :emb_dim], dtype=torch.float32)

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for x, _ in loader:
            optimizer.zero_grad()
            emb = model(x)
            labels = km.predict(x.numpy().astype(np.float32))  # Fix: ensure float32 here
            target = centers[torch.tensor(labels)]
            loss = criterion(emb, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}, Loss: {total_loss/len(loader):.4f}")
    return model, dataset


# Visualize embeddings
def visualize(model, dataset, label_to_idx):
    model.eval()
    loader = DataLoader(dataset, batch_size=32)
    X, Y = [], []
    with torch.no_grad():
        for x, y in loader:
            X.append(model(x).numpy())
            Y += y.numpy().tolist()
    X = np.vstack(X)
    Y = np.array(Y)

    tsne = TSNE(n_components=2, random_state=42)
    X_2d = tsne.fit_transform(X)

    plt.figure(figsize=(10, 6))
    for label_idx in np.unique(Y):
        idxs = (Y == label_idx)
        plt.scatter(X_2d[idxs, 0], X_2d[idxs, 1], label=list(label_to_idx.keys())[label_idx], alpha=0.7)
    plt.legend()
    plt.title("t-SNE of Time Spread Embeddings")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Run all
data, label_map = generate_activity_data()
model, dataset = train_unsup_model(data)
visualize(model, dataset, label_map)

import matplotlib.pyplot as plt

# Extract activity labels and raw timestamps from synthetic data
from collections import defaultdict
import seaborn as sns

# Group timestamps by label
label_to_ts = defaultdict(list)
for ts_seq, label in synthetic_data:
    label_to_ts[label].append(ts_seq)

# Plot distributions
plt.figure(figsize=(12, 6))
for label, sequences in label_to_ts.items():
    # Flatten and filter valid timestamps (non-zero)
    flat = [t for seq in sequences for t in seq if t > 0]
    hours = [(t % 86400) / 3600 for t in flat]  # convert to hour of day
    sns.kdeplot(hours, label=label, fill=True)

plt.xlabel("Hour of Day")
plt.ylabel("Density")
plt.title("Temporal Activity Patterns by Activity Type")
plt.legend()
plt.grid(True)
plt.show()
