import random
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# --- Helper Functions ---
def random_time(start, end):
    """Generate a random datetime between two datetimes."""
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def generate_face_data(num_faces):
    faces = []
    for _ in range(num_faces):
        face_id = str(uuid.uuid4())
        age = random.randint(1, 80)
        gender = random.choice(["male", "female"])
        bbox = {
            "x": random.randint(0, 500),
            "y": random.randint(0, 500),
            "width": random.randint(50, 100),
            "height": random.randint(50, 100)
        }
        faces.append({
            "face_id": face_id,
            "age": age,
            "gender": gender,
            "bbox": bbox
        })
    return faces

def growth_kernel(t, t0=0, slope=0.05):
    return slope * (t - t0)

def decay_kernel(t, t0=0, alpha=0.5):
    return alpha * np.exp(-0.1 * (t - t0))

def stable_kernel(t, base=0.2):
    return base

# --- Image Event Simulation ---
def simulate_images(user_id, start_date, num_days, behavior_type, poi_list, scene_list, max_per_day=5):
    image_data = []
    base_time = datetime.strptime(start_date, "%Y-%m-%d")

    for day in range(num_days):
        date = base_time + timedelta(days=day)
        # Determine intensity
        if behavior_type == "growing":
            intensity = min(int(growth_kernel(day) * max_per_day), max_per_day)
        elif behavior_type == "decaying":
            intensity = max(1, int(decay_kernel(day) * max_per_day))
        else:
            intensity = int(stable_kernel(day) * max_per_day)

        for _ in range(intensity):
            timestamp = random_time(date, date + timedelta(days=1))
            location = {
                "lat": round(random.uniform(-90, 90), 6),
                "lon": round(random.uniform(-180, 180), 6),
                "poi": random.choice(poi_list),
                "city": random.choice(["NYC", "LA", "SF", "Chicago"]),
                "state": random.choice(["NY", "CA", "IL"]),
                "country": "USA"
            }
            faces = generate_face_data(random.randint(1, 3))
            scene = random.choice(scene_list)
            image_data.append({
                "user_id": user_id,
                "timestamp": timestamp,
                "location": location,
                "faces": faces,
                "scene": scene,
                "ground_truth": f"routine:{behavior_type}"
            })
    return image_data



# --- Run Simulation for One User ---
user_id = "U001"
start_date = "2025-06-01"
num_days = 30
poi_list = ["Home", "Office", "Park", "Mall", "Beach"]
scene_list = ["indoor", "outdoor", "nature", "urban"]

# Simulate different behaviors
images_growing = simulate_images(user_id, start_date, num_days, "growing", poi_list, scene_list)
images_decaying = simulate_images(user_id, start_date, num_days, "decaying", poi_list, scene_list)
images_stable = simulate_images(user_id, start_date, num_days, "stable", poi_list, scene_list)

# Combine all
all_images = images_growing + images_decaying + images_stable

# Convert to DataFrame (simplified for tabular view)
df_images = pd.DataFrame([{
    "user_id": img["user_id"],
    "timestamp": img["timestamp"],
    "lat": img["location"]["lat"],
    "lon": img["location"]["lon"],
    "poi": img["location"]["poi"],
    "city": img["location"]["city"],
    "state": img["location"]["state"],
    "country": img["location"]["country"],
    "scene": img["scene"],
    "face_ids": [f["face_id"] for f in img["faces"]],
    "ground_truth": img["ground_truth"]
} for img in all_images])

df_images.head()


import numpy as np
import pandas as pd
import random
import uuid
from datetime import datetime, timedelta

# --- Core Time Model ---
def generate_time_range(start_date, num_days):
    base_time = datetime.strptime(start_date, "%Y-%m-%d")
    return [base_time + timedelta(days=i) for i in range(num_days)]

# --- Kernel Functions ---
def intensity_function(behavior_type, t, t0=0, base=0.5, alpha=0.5, slope=0.05):
    if behavior_type == "growing":
        return min(1.0, slope * (t - t0))
    elif behavior_type == "decaying":
        return max(0.1, alpha * np.exp(-0.1 * (t - t0)))
    else:
        return base

# --- Users and Contact Metadata ---
def generate_user_profiles(n_users):
    users = []
    for i in range(n_users):
        user_id = f"U{str(i+1).zfill(3)}"
        contacts = [f"C{str(j+1).zfill(3)}" for j in range(5)]
        relations = ["friend", "colleague", "family", "acquaintance", "partner"]
        contact_book = [{
            "contact_id": c,
            "relation": random.choice(relations)
        } for c in contacts]
        users.append({
            "user_id": user_id,
            "contacts": contact_book
        })
    return users

# --- Call Logs Generator ---
def simulate_call_logs(users, start_date, num_days, behavior_type):
    logs = []
    for user in users:
        for day in range(num_days):
            intensity = int(10 * intensity_function(behavior_type, day))
            for _ in range(intensity):
                timestamp = random_time(
                    datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day),
                    datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day+1)
                )
                contact = random.choice(user["contacts"])
                duration = random.randint(30, 300)
                logs.append({
                    "user_id": user["user_id"],
                    "timestamp": timestamp,
                    "callee": contact["contact_id"],
                    "duration_sec": duration,
                    "relation": contact["relation"],
                    "ground_truth": f"social:{behavior_type}"
                })
    return logs

# --- App Usage Generator ---
def simulate_app_usage(users, start_date, num_days, behavior_type, apps=["YouTube", "Gmail", "Instagram", "Maps"]):
    logs = []
    for user in users:
        for day in range(num_days):
            intensity = int(10 * intensity_function(behavior_type, day))
            for _ in range(intensity):
                timestamp = random_time(
                    datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day),
                    datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day+1)
                )
                app = random.choice(apps)
                duration = random.randint(1, 30)
                logs.append({
                    "user_id": user["user_id"],
                    "timestamp": timestamp,
                    "app": app,
                    "duration_min": duration,
                    "ground_truth": f"interest:{behavior_type}"
                })
    return logs

# --- Calendar Events Generator ---
def simulate_calendar_events(users, start_date, num_days, behavior_type, event_types=["meeting", "gym", "birthday", "travel", "study"]):
    logs = []
    for user in users:
        for day in range(num_days):
            intensity = int(5 * intensity_function(behavior_type, day))
            for _ in range(intensity):
                timestamp = random_time(
                    datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day),
                    datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day+1)
                )
                event = random.choice(event_types)
                location = random.choice(["Home", "Work", "Cafe", "Gym"])
                logs.append({
                    "user_id": user["user_id"],
                    "timestamp": timestamp,
                    "event_type": event,
                    "location": location,
                    "ground_truth": f"routine:{behavior_type}"
                })
    return logs

# --- Simulation Execution ---
NUM_USERS = 3
NUM_DAYS = 30
START_DATE = "2025-06-01"

users = generate_user_profiles(NUM_USERS)

# Simulate each modality for all behavior types
call_logs = simulate_call_logs(users, START_DATE, NUM_DAYS, "growing") + \
            simulate_call_logs(users, START_DATE, NUM_DAYS, "decaying") + \
            simulate_call_logs(users, START_DATE, NUM_DAYS, "stable")

app_usage = simulate_app_usage(users, START_DATE, NUM_DAYS, "growing") + \
            simulate_app_usage(users, START_DATE, NUM_DAYS, "decaying") + \
            simulate_app_usage(users, START_DATE, NUM_DAYS, "stable")

calendar_events = simulate_calendar_events(users, START_DATE, NUM_DAYS, "growing") + \
                  simulate_calendar_events(users, START_DATE, NUM_DAYS, "decaying") + \
                  simulate_calendar_events(users, START_DATE, NUM_DAYS, "stable")

# Convert to DataFrames
df_calls = pd.DataFrame(call_logs)
df_apps = pd.DataFrame(app_usage)
df_calendar = pd.DataFrame(calendar_events)

