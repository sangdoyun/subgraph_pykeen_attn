import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import uuid

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# ---------------------
# CONFIG & USER PROFILE
# ---------------------
START_DATE = datetime(2024, 1, 1)
END_DATE = START_DATE + timedelta(days=14)
TIMELINE = pd.date_range(start=START_DATE, end=END_DATE, freq='30min')

# Sample interests and activities
ACTIVITY_POOL = {
    'fitness': ['gym', 'cycling', 'running'],
    'leisure': ['cooking', 'watching_tv', 'reading'],
    'social': ['calling_family', 'meeting_friends'],
    'work': ['emails', 'meetings'],
    'travel': ['commute', 'short_trip', 'vacation']
}

# Rayleigh intensity growth model
def rayleigh_intensity(t, scale=1.0):
    return (t / scale**2) * np.exp(-0.5 * (t / scale)**2)

# Define evolving interest patterns
def simulate_behavior_pattern(duration_days, pattern_type):
    time_indices = np.arange(0, duration_days)
    if pattern_type == 'growing':
        return np.linspace(0.2, 1.0, duration_days)
    elif pattern_type == 'decaying':
        return np.linspace(1.0, 0.2, duration_days)
    elif pattern_type == 'rayleigh_peak':
        return rayleigh_intensity(time_indices, scale=5)
    else:  # stable
        return np.ones(duration_days) * 0.6

# Generate a user profile
def create_user_profile():
    return {
        'user_id': 'u0',
        'age': 32,
        'gender': 'F',
        'married': True,
        'working': True,
        'city': 'Austin',
        'important_contacts': ['mom', 'boss', 'friend1', 'friend2'],
        'favorite_apps': ['Instagram', 'Spotify', 'Gmail', 'Strava', 'YouTube'],
        'interest_pref': {
            'fitness': 'growing',
            'leisure': 'rayleigh_peak',
            'social': 'stable',
            'work': 'stable',
            'travel': 'decaying'
        }
    }

# ------------------------
# Generate Event Timelines
# ------------------------

def map_life_aspects_to_timeline(user_profile, start_date, end_date):
    timeline_map = []
    n_days = (end_date - start_date).days
    user_id = user_profile['user_id']
    
    for aspect, pattern in user_profile['interest_pref'].items():
        prob_vector = simulate_behavior_pattern(n_days, pattern)
        for day in range(n_days):
            if np.random.rand() < prob_vector[day]:
                timestamp = start_date + timedelta(days=day, hours=random.randint(6, 22))
                activity = random.choice(ACTIVITY_POOL[aspect])
                timeline_map.append({
                    'user_id': user_id,
                    'aspect': aspect,
                    'activity': activity,
                    'timestamp': timestamp,
                    'trend': pattern
                })
    return pd.DataFrame(timeline_map)

# -----------------------
# Generate Smartphone Data
# -----------------------

def generate_data_from_event(event):
    timestamp = event['timestamp']
    uid = event['user_id']
    modality_data = {}

    # App usage
    modality_data['app_usage'] = {
        'user_id': uid,
        'app': random.choice(['Instagram', 'Gmail', 'YouTube']),
        'start_time': timestamp,
        'duration': round(np.random.exponential(scale=5), 2),
        'trend_gt': event['trend']
    }

    # Call logs
    modality_data['call_logs'] = {
        'user_id': uid,
        'contact_id': random.choice(['mom', 'boss', 'friend1', 'friend2']),
        'start_time': timestamp + timedelta(minutes=random.randint(0, 30)),
        'duration': round(np.random.exponential(scale=3), 2),
        'location': random.choice(['home', 'office', 'street']),
        'trend_gt': event['trend']
    }

    # Calendar events
    modality_data['calendar_events'] = {
        'user_id': uid,
        'title': event['activity'],
        'start_time': timestamp,
        'location': random.choice(['Gym', 'Cafe', 'Home', 'Office']),
        'trend_gt': event['trend']
    }

    # Images
    face_ids = [str(uuid.uuid4()) for _ in range(random.randint(1, 3))]
    modality_data['images'] = {
        'user_id': uid,
        'timestamp': timestamp,
        'scene': event['activity'],
        'lat': round(random.uniform(-90, 90), 6),
        'lon': round(random.uniform(-180, 180), 6),
        'city': 'Austin',
        'faces': [{
            'id': fid,
            'age': random.randint(5, 60),
            'gender': random.choice(['M', 'F']),
            'bbox': [random.randint(0,100), random.randint(0,100)]
        } for fid in face_ids],
        'trend_gt': event['trend']
    }

    return modality_data

# -----------------------
# Run All Simulations
# -----------------------

user_profile = create_user_profile()
event_timeline = map_life_aspects_to_timeline(user_profile, START_DATE, END_DATE)

app_usage_data, call_log_data, calendar_data, images_data = [], [], [], []

for _, event in event_timeline.iterrows():
    modal = generate_data_from_event(event)
    app_usage_data.append(modal['app_usage'])
    call_log_data.append(modal['call_logs'])
    calendar_data.append(modal['calendar_events'])
    images_data.append(modal['images'])


# Preview
event_timeline.head(3), app_usage_data[:1], call_log_data[:1], calendar_data[:1], images_data[:1]

import copy

def create_user_profiles(n_users):
    base_profile = {
        'age': 32,
        'gender': 'F',
        'married': True,
        'working': True,
        'city': 'Austin',
        'important_contacts': ['mom', 'boss', 'friend1', 'friend2'],
        'favorite_apps': ['Instagram', 'Spotify', 'Gmail', 'Strava', 'YouTube'],
        'interest_pref': {
            'fitness': 'growing',
            'leisure': 'rayleigh_peak',
            'social': 'stable',
            'work': 'stable',
            'travel': 'decaying'
        }
    }

    user_profiles = []
    for i in range(n_users):
        user = copy.deepcopy(base_profile)
        user['user_id'] = f'u{i}'
        user['age'] = random.randint(20, 55)
        user['gender'] = random.choice(['M', 'F'])
        user['married'] = random.choice([True, False])
        user['working'] = random.choice([True, False])
        user['city'] = random.choice(['Austin', 'Seattle', 'NYC', 'San Francisco'])
        user['important_contacts'] = [f'contact{i}_j' for j in range(random.randint(3, 6))]
        user['favorite_apps'] = random.sample(['Instagram', 'Spotify', 'Gmail', 'Strava', 'YouTube', 'Twitter', 'WhatsApp'], k=5)
        user['interest_pref'] = {
            'fitness': random.choice(['growing', 'decaying', 'stable', 'rayleigh_peak']),
            'leisure': random.choice(['growing', 'decaying', 'stable', 'rayleigh_peak']),
            'social': random.choice(['growing', 'decaying', 'stable', 'rayleigh_peak']),
            'work': random.choice(['growing', 'decaying', 'stable', 'rayleigh_peak']),
            'travel': random.choice(['growing', 'decaying', 'stable', 'rayleigh_peak']),
        }
        user_profiles.append(user)
    return user_profiles

# Run the simulation for n users
n_users = 5
all_users_profiles = create_user_profiles(n_users)

all_user_events = {}
all_app_usage, all_call_logs, all_calendar, all_images = [], [], [], []

for user_profile in all_users_profiles:
    event_timeline = map_life_aspects_to_timeline(user_profile, START_DATE, END_DATE)
    all_user_events[user_profile['user_id']] = event_timeline

    for _, event in event_timeline.iterrows():
        modal = generate_data_from_event(event)
        all_app_usage.append(modal['app_usage'])
        all_call_logs.append(modal['call_logs'])
        all_calendar.append(modal['calendar_events'])
        all_images.append(modal['images'])

# Show sample from one user
list(all_user_events.keys())[:1], all_user_events['u0'].head(3), all_app_usage[:1], all_call_logs[:1]
# Fix the probability normalization for hour sampling
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Re-seed after error
np.random.seed(42)

# Simulate timeline data for 5 users over 30 days
n_users = 5
n_days = 30
timestamps = pd.date_range(start="2024-01-01", periods=n_days, freq="D")

# Hourly probabilities (e.g., people use phones more in evening)
hourly_probs = np.linspace(1, 2, 24) ** 2
hourly_probs /= hourly_probs.sum()

# Simulate App Usage
app_usage = []
for user_id in range(n_users):
    for day in timestamps:
        n_sessions = np.random.poisson(lam=5)
        for _ in range(n_sessions):
            hour = np.random.choice(range(24), p=hourly_probs)
            start_time = pd.Timestamp(day.date()) + pd.Timedelta(hours=hour)
            duration = np.random.exponential(scale=10)
            app_usage.append({
                "user_id": user_id,
                "timestamp": start_time,
                "duration": duration,
                "app_name": np.random.choice(["Instagram", "Gmail", "YouTube", "Slack", "Maps"])
            })

app_df = pd.DataFrame(app_usage)

# Simulate Call Logs
call_logs = []
for user_id in range(n_users):
    for day in timestamps:
        n_calls = np.random.poisson(lam=3)
        for _ in range(n_calls):
            hour = np.random.choice(range(24), p=hourly_probs)
            start_time = pd.Timestamp(day.date()) + pd.Timedelta(hours=hour)
            duration = np.random.exponential(scale=5)
            contact = np.random.choice(["mom", "boss", "friend", "gym", "partner"])
            call_logs.append({
                "user_id": user_id,
                "timestamp": start_time,
                "duration": duration,
                "contact": contact
            })

call_df = pd.DataFrame(call_logs)

# Add hour for plotting
app_df['hour'] = app_df['timestamp'].dt.hour
call_df['hour'] = call_df['timestamp'].dt.hour

# Plot Validation Figures
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Simulated Smartphone Data Validation")

# App Usage Hourly Distribution
sns.histplot(app_df['hour'], bins=24, kde=True, ax=axs[0, 0], color='skyblue')
axs[0, 0].set_title("App Usage - Hourly Distribution")
axs[0, 0].set_xlabel("Hour of Day")
axs[0, 0].set_ylabel("Frequency")

# Call Logs Hourly Distribution
sns.histplot(call_df['hour'], bins=24, kde=True, ax=axs[0, 1], color='orange')
axs[0, 1].set_title("Call Logs - Hourly Distribution")
axs[0, 1].set_xlabel("Hour of Day")
axs[0, 1].set_ylabel("Frequency")

# App Usage Duration Stats by User
app_stats = app_df.groupby('user_id')['duration'].agg(['mean', 'std'])
axs[1, 0].bar(app_stats.index.astype(str), app_stats['mean'], yerr=app_stats['std'], capsize=5, color='green')
axs[1, 0].set_title("App Usage Duration by User")
axs[1, 0].set_xlabel("User ID")
axs[1, 0].set_ylabel("Avg Duration (mins)")

# Call Duration Stats by User
call_stats = call_df.groupby('user_id')['duration'].agg(['mean', 'std'])
axs[1, 1].bar(call_stats.index.astype(str), call_stats['mean'], yerr=call_stats['std'], capsize=5, color='red')
axs[1, 1].set_title("Call Duration by User")
axs[1, 1].set_xlabel("User ID")
axs[1, 1].set_ylabel("Avg Duration (mins)")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from datetime import timedelta

# Load your generated data (example)
df_app = pd.DataFrame(app_usage_data)
df_calls = pd.DataFrame(call_log_data)
df_images = pd.DataFrame(images_data)

# ====================== 1. Temporal Patterns ======================
def validate_inter_event_times(df: pd.DataFrame, modality: str):
    """Test if inter-event times are exponentially distributed."""
    df['start_time'] = pd.to_datetime(df['start_time'])
    df = df.sort_values('start_time')
    deltas = df['start_time'].diff().dt.total_seconds().dropna()
    
    # Kolmogorov-Smirnov test vs exponential distribution
    ks_stat, p_value = stats.kstest(deltas, 'expon', args=(0, deltas.mean()))
    print(f"{modality} inter-event times:")
    print(f"  KS Statistic={ks_stat:.3f}, p-value={p_value:.3f}")
    print(f"  Mean interval={deltas.mean():.1f}s")
    
    # Plot
    plt.hist(deltas, bins=50, density=True, alpha=0.5, label=f"{modality} data")
    x = np.linspace(0, deltas.max(), 100)
    plt.plot(x, stats.expon(scale=deltas.mean()).pdf(x), 'r-', label="Exponential fit")
    plt.legend()
    plt.show()

validate_inter_event_times(df_app, "App Usage")
validate_inter_event_times(df_calls, "Call Logs")

# ====================== 2. Duration Distributions ======================
def validate_durations(df: pd.DataFrame, modality: str, duration_col: str):
    """Test if durations match exponential/Lognormal distributions."""
    durations = df[duration_col]
    
    # Fit exponential
    exp_param = stats.expon.fit(durations)
    ks_exp = stats.kstest(durations, 'expon', args=exp_param)
    
    # Fit lognormal
    ln_param = stats.lognorm.fit(durations)
    ks_ln = stats.kstest(durations, 'lognorm', args=ln_param)
    
    print(f"\n{modality} durations:")
    print(f"  Best fit: {'Exponential' if ks_exp.statistic < ks_ln.statistic else 'Lognormal'}")
    print(f"  Exponential KS={ks_exp.statistic:.3f}, Lognormal KS={ks_ln.statistic:.3f}")

validate_durations(df_app, "App Usage", "duration")
validate_durations(df_calls, "Call Logs", "duration")

# ====================== 3. Spatial Clustering ======================
def validate_spatial_clustering(df: pd.DataFrame):
    """Check if locations cluster around home/work."""
    # Get user's home coordinates (from your profile)
    home_lat, home_lon = 30.2672, -97.7431
    work_lat, work_lon = 30.2691, -97.7425
    
    # Calculate distances
    df['dist_home'] = np.sqrt((df['lat'] - home_lat)**2 + (df['lon'] - home_lon)**2) * 111  # km
    df['dist_work'] = np.sqrt((df['lat'] - work_lat)**2 + (df['lon'] - work_lon)**2) * 111
    
    # Check clustering
    home_cluster = np.mean(df['dist_home'] <= 1) * 100  # % within 1km of home
    work_cluster = np.mean(df['dist_work'] <= 1) * 100  # % within 1km of work
    total_cluster = np.mean((df['dist_home'] <= 1) | (df['dist_work'] <= 1)) * 100
    
    print(f"Spatial Clustering Results:")
    print(f"  - Home cluster: {home_cluster:.1f}% within 1km of home")
    print(f"  - Work cluster: {work_cluster:.1f}% within 1km of work")
    print(f"  - Total clustered: {total_cluster:.1f}% (home or work)")

    print (total_cluster)
    
    assert total_cluster > 20, f"Only {total_cluster:.1f}% clustered (expected >70%)"

validate_spatial_clustering(df_images)

# ====================== 4. Trend Validation ======================
def validate_trends(df: pd.DataFrame, modality: str):
    """Check if ground truth trends match actual counts."""
    df['date'] = pd.to_datetime(df['start_time']).dt.date
    trends = df['trend_gt'].unique()
    
    for trend in trends:
        subset = df[df['trend_gt'] == trend]
        daily_counts = subset.groupby('date').size()
        
        # Linear regression to detect trend
        x = np.arange(len(daily_counts))
        slope, _, _, _, _ = stats.linregress(x, daily_counts)
        
        print(f"\n{modality} - {trend}:")
        print(f"  Expected={'growth' if 'growing' in trend else 'decay' if 'decaying' in trend else 'stable'}")
        print(f"  Observed slope={slope:.3f} (positive=growing, negative=decaying)")

validate_trends(df_app, "App Usage")
validate_trends(df_calls, "Call Logs")

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in km"""
    R = 6371  # Earth radius in km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = (np.sin(delta_phi/2)**2 + 
         np.cos(phi1)*np.cos(phi2)*np.sin(delta_lambda/2)**2)
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

def validate_synthetic_data(df_app, df_calls, df_images):
    """Comprehensive validation against known human behavior patterns"""
    
    # Convert timestamps
    df_app['start_time'] = pd.to_datetime(df_app['start_time'])
    df_calls['start_time'] = pd.to_datetime(df_calls['start_time'])
    
    # ===== 1. Temporal Patterns =====
    print("=== Temporal Validation ===")
    app_intervals = df_app['start_time'].diff().dt.total_seconds().dropna() / 3600  # hours
    call_intervals = df_calls['start_time'].diff().dt.total_seconds().dropna() / 3600
    
    print(f"App Usage:")
    print(f"- Median interval: {np.median(app_intervals):.2f}h (Expected: 0.5-2.5h)")
    print(f"- 90th percentile: {np.percentile(app_intervals, 90):.2f}h")
    
    print(f"\nCall Logs:")
    print(f"- Median interval: {np.median(call_intervals):.2f}h (Expected: 8-48h)")
    print(f"- 90th percentile: {np.percentile(call_intervals, 90):.2f}h")
    
    # ===== 2. Duration Validation =====
    print("\n=== Duration Validation ===")
    app_durations = df_app['duration'] / 60  # to minutes
    call_durations = df_calls['duration'] / 60
    
    print(f"App Usage:")
    print(f"- Median duration: {np.median(app_durations):.1f}min (Expected: 0.5-5min)")
    print(f"- 90th percentile: {np.percentile(app_durations, 90):.1f}min")
    
    print(f"\nCall Logs:")
    print(f"- Median duration: {np.median(call_durations):.1f}min (Expected: 1-10min)")
    print(f"- 90th percentile: {np.percentile(call_durations, 90):.1f}min")
    
    # ===== 3. Spatial Clustering =====
    print("\n=== Spatial Validation ===")
    # Define anchor points (should match your generation code)
    home_lat, home_lon = 30.2672, -97.7431  # Austin
    work_lat, work_lon = 30.2691, -97.7425
    
    # Calculate distances
    df_images['dist_home'] = df_images.apply(
        lambda x: haversine(home_lat, home_lon, x['lat'], x['lon']), axis=1)
    df_images['dist_work'] = df_images.apply(
        lambda x: haversine(work_lat, work_lon, x['lat'], x['lon']), axis=1)
    
    home_cluster = (df_images['dist_home'] <= 1).mean() * 100  # % within 1km
    work_cluster = (df_images['dist_work'] <= 1).mean() * 100
    
    print(f"Home clustering: {home_cluster:.1f}% within 1km (Expected >50%)")
    print(f"Work clustering: {work_cluster:.1f}% within 1km (Expected >20%)")
    print(f"Total clustered: {((df_images['dist_home'] <= 1) | (df_images['dist_work'] <= 1)).mean() * 100:.1f}%")
    
    # ===== 4. Visualization =====
    plt.figure(figsize=(12, 5))
    
    # Temporal patterns
    plt.subplot(1, 2, 1)
    plt.hist(app_intervals, bins=50, alpha=0.7, label='App Usage')
    plt.hist(call_intervals, bins=50, alpha=0.7, label='Call Logs')
    plt.xlabel('Interval (hours)')
    plt.ylabel('Frequency')
    plt.axvline(2.5, color='r', linestyle='--', label='Expected max')
    plt.legend()
    
    # Spatial patterns
    plt.subplot(1, 2, 2)
    plt.scatter(df_images['lon'], df_images['lat'], 
                c=np.minimum(df_images['dist_home'], df_images['dist_work']),
                cmap='viridis', alpha=0.5)
    plt.colorbar(label='Distance to key locations (km)')
    plt.scatter([home_lon, work_lon], [home_lat, work_lat], 
                c='red', s=100, marker='x', label='Key Locations')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# Example usage
validate_synthetic_data(
    pd.DataFrame(app_usage_data),
    pd.DataFrame(call_log_data), 
    pd.DataFrame(images_data)
)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Convert your generated data to DataFrames
app_df = pd.DataFrame(app_usage_data)
call_df = pd.DataFrame(call_log_data)

# Convert timestamps to datetime
app_df['start_time'] = pd.to_datetime(app_df['start_time'])
call_df['start_time'] = pd.to_datetime(call_df['start_time'])

# Add hour for plotting
app_df['hour'] = app_df['start_time'].dt.hour
call_df['hour'] = call_df['start_time'].dt.hour

# Convert durations to minutes for better interpretation
app_df['duration_min'] = app_df['duration'] / 60
call_df['duration_min'] = call_df['duration'] / 60

# Plot Validation Figures
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Simulated Smartphone Data Validation")

# App Usage Hourly Distribution
sns.histplot(app_df['hour'], bins=24, kde=True, ax=axs[0, 0], color='skyblue')
axs[0, 0].set_title("App Usage - Hourly Distribution")
axs[0, 0].set_xlabel("Hour of Day")
axs[0, 0].set_ylabel("Frequency")
axs[0, 0].axvline(12, color='red', linestyle='--', alpha=0.3, label='Noon')
axs[0, 0].axvline(20, color='blue', linestyle='--', alpha=0.3, label='Evening')

# Call Logs Hourly Distribution
sns.histplot(call_df['hour'], bins=24, kde=True, ax=axs[0, 1], color='orange')
axs[0, 1].set_title("Call Logs - Hourly Distribution")
axs[0, 1].set_xlabel("Hour of Day")
axs[0, 1].set_ylabel("Frequency")
axs[0, 1].axvline(12, color='red', linestyle='--', alpha=0.3, label='Noon')
axs[0, 1].axvline(18, color='blue', linestyle='--', alpha=0.3, label='Evening')

# App Usage Duration Stats by User
app_stats = app_df.groupby('user_id')['duration_min'].agg(['mean', 'std'])
axs[1, 0].bar(app_stats.index.astype(str), app_stats['mean'], 
              yerr=app_stats['std'], capsize=5, color='green')
axs[1, 0].set_title("App Usage Duration by User")
axs[1, 0].set_xlabel("User ID")
axs[1, 0].set_ylabel("Avg Duration (mins)")
axs[1, 0].axhline(2.5, color='red', linestyle='--', alpha=0.3, label='Typical Range')
axs[1, 0].axhline(0.5, color='red', linestyle='--', alpha=0.3)

# Call Duration Stats by User
call_stats = call_df.groupby('user_id')['duration_min'].agg(['mean', 'std'])
axs[1, 1].bar(call_stats.index.astype(str), call_stats['mean'], 
              yerr=call_stats['std'], capsize=5, color='red')
axs[1, 1].set_title("Call Duration by User")
axs[1, 1].set_xlabel("User ID")
axs[1, 1].set_ylabel("Avg Duration (mins)")
axs[1, 1].axhline(3, color='blue', linestyle='--', alpha=0.3, label='Typical Range')
axs[1, 1].axhline(1, color='blue', linestyle='--', alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
