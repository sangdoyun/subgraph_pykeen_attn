# Remove haversine dependency since it's not used in current code
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from datetime import datetime

# Simulated df_pic data for moment detection
df_pic = pd.DataFrame({
    "id": ["a1", "a2", "a3", "a4", "a5", "a6"],
    "start_time": pd.to_datetime([
        "2023-01-01T10:00", "2023-01-01T10:10", "2023-01-01T10:30",
        "2023-01-01T15:00", "2023-01-01T15:15", "2023-01-01T15:40"
    ]),
    "end_time": pd.to_datetime([
        "2023-01-01T10:05", "2023-01-01T10:20", "2023-01-01T10:35",
        "2023-01-01T15:10", "2023-01-01T15:25", "2023-01-01T15:50"
    ]),
    "images": [["img1", "img2"], ["img3"], ["img4"], ["img5", "img6", "img7"], ["img8"], ["img9"]],
    "location": ["Paris"] * 6,
    "lat": [48.8584, 48.8585, 48.8586, 48.8600, 48.8602, 48.8603],
    "lon": [2.2945, 2.2946, 2.2947, 2.2950, 2.2951, 2.2952],
    "scenes": [["monument", "group"], ["group"], ["selfie"], ["sunset"], ["monument"], ["monument"]],
    "faces": [["f1", "f2"], ["f1", "f2"], ["f1"], ["f2", "f3"], ["f2"], ["f2"]]
})

# Feature computation
df_pic["duration"] = (df_pic["end_time"] - df_pic["start_time"]).dt.total_seconds()
df_pic["face_count"] = df_pic["faces"].apply(len)
df_pic["scene_count"] = df_pic["scenes"].apply(lambda x: len(set(x)))
df_pic["image_count"] = df_pic["images"].apply(len)
df_pic["center_time"] = df_pic["start_time"] + (df_pic["end_time"] - df_pic["start_time"]) / 2
df_pic["timestamp"] = df_pic["center_time"].astype(np.int64) // 10**9

# Spatial-temporal clustering
X = df_pic[["timestamp", "lat", "lon"]]
X_scaled = StandardScaler().fit_transform(X)
dbscan = DBSCAN(eps=1.0, min_samples=2).fit(X_scaled)
df_pic["cluster"] = dbscan.labels_

# Aggregate clusters into moments
moments = []
for c_id in sorted(df_pic["cluster"].unique()):
    if c_id == -1:
        continue
    group = df_pic[df_pic["cluster"] == c_id]
    start = group["start_time"].min()
    end = group["end_time"].max()
    loc = group["location"].mode()[0]
    scenes = list(set([s for sub in group["scenes"] for s in sub]))
    faces = list(set([f for sub in group["faces"] for f in sub]))
    images = list(set([i for sub in group["images"] for i in sub]))
    score = (
        0.3 * group["face_count"].sum() +
        0.25 * len(scenes) +
        0.2 * group["image_count"].sum() +
        0.15 * group["duration"].sum() +
        0.1 * np.mean(group["timestamp"])
    ) / 100  # normalization for scale
    moments.append({
        "moment_id": f"m{c_id}",
        "start_time": start,
        "end_time": end,
        "location": loc,
        "scenes": scenes,
        "faces": faces,
        "images": images,
        "score": round(score, 3)
    })

moments
