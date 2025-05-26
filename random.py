
import pandas as pd
import random
from datetime import datetime, timedelta

# Dates from Sept 1 to Sept 10
date_range = [datetime(2024, 9, 1) + timedelta(days=i) for i in range(10)]

# Define City for each day
city_by_day = ["City1"]*4 + ["City2"]*4 + ["City1"]*2

# Simulate data tables
images_data = []
calls_data = []
location_data = []
payments_data = []

for i, date in enumerate(date_range):
    date_str = date.strftime('%Y-%m-%d')
    city = city_by_day[i]
    
    # Simulate images
    for j in range(random.randint(1, 3 if city == "City2" else 1)):
        images_data.append({
            "date": date_str,
            "image_id": f"img_{i}_{j}",
            "scene": random.choice(["monument", "food", "cityscape", "selfie"]),
            "faces": random.choice(["solo", "family", "group"]),
            "location": city
        })
    
    # Simulate calls
    for j in range(random.randint(1, 2)):
        calls_data.append({
            "date": date_str,
            "call_id": f"call_{i}_{j}",
            "duration_min": random.choice([2, 5, 10, 15]),
            "contact": random.choice(["Home", "Friend", "Work", "Hotel"]),
            "location": city
        })
    
    # Location ping (once per day)
    location_data.append({
        "date": date_str,
        "lat": random.uniform(28.60, 28.62) if city == "City1" else random.uniform(48.85, 48.87),
        "lon": random.uniform(77.20, 77.22) if city == "City1" else random.uniform(2.35, 2.37),
        "city": city
    })
    
    # Simulate payments
    for j in range(random.randint(1, 2 if city == "City2" else 1)):
        payments_data.append({
            "date": date_str,
            "merchant": random.choice(["Cafe", "Uber", "Museum", "Restaurant", "Store"]),
            "amount": random.randint(5, 50),
            "location": city
        })

# Convert to DataFrames
df_images = pd.DataFrame(images_data)
df_calls = pd.DataFrame(calls_data)
df_location = pd.DataFrame(location_data)
df_payments = pd.DataFrame(payments_data)

df_images.head(), df_calls.head(), df_location.head(), df_payments.head()


import pandas as pd
import random
from datetime import datetime, timedelta
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import XSD

# Re-generate the previously created data
date_range = [datetime(2024, 9, 1) + timedelta(days=i) for i in range(10)]
city_by_day = ["City1"]*4 + ["City2"]*4 + ["City1"]*2
images_data, calls_data, location_data, payments_data = [], [], [], []

for i, date in enumerate(date_range):
    date_str = date.strftime('%Y-%m-%d')
    city = city_by_day[i]

    for j in range(random.randint(1, 3 if city == "City2" else 1)):
        images_data.append({
            "date": date_str,
            "image_id": f"img_{i}_{j}",
            "scene": random.choice(["monument", "food", "cityscape", "selfie"]),
            "faces": random.choice(["solo", "family", "group"]),
            "location": city
        })

    for j in range(random.randint(1, 2)):
        calls_data.append({
            "date": date_str,
            "call_id": f"call_{i}_{j}",
            "duration_min": random.choice([2, 5, 10, 15]),
            "contact": random.choice(["Home", "Friend", "Work", "Hotel"]),
            "location": city
        })

    location_data.append({
        "date": date_str,
        "lat": random.uniform(28.60, 28.62) if city == "City1" else random.uniform(48.85, 48.87),
        "lon": random.uniform(77.20, 77.22) if city == "City1" else random.uniform(2.35, 2.37),
        "city": city
    })

    for j in range(random.randint(1, 2 if city == "City2" else 1)):
        payments_data.append({
            "date": date_str,
            "merchant": random.choice(["Cafe", "Uber", "Museum", "Restaurant", "Store"]),
            "amount": random.randint(5, 50),
            "location": city
        })

df_images = pd.DataFrame(images_data)
df_calls = pd.DataFrame(calls_data)
df_location = pd.DataFrame(location_data)
df_payments = pd.DataFrame(payments_data)

# Define Namespaces for TKG
NS = Namespace("http://example.org/")
IMG = Namespace("http://example.org/image/")
CALL = Namespace("http://example.org/call/")
LOC = Namespace("http://example.org/location/")
PAY = Namespace("http://example.org/payment/")
TIME = Namespace("http://example.org/time/")
REL = Namespace("http://example.org/relation/")
SCN = Namespace("http://example.org/scene/")
FACE = Namespace("http://example.org/face/")

# Function to create a daily TKG
def create_daily_tkg(date_str):
    g = Graph()
    g.bind("ns", NS)
    for row in df_images[df_images["date"] == date_str].itertuples():
        img = URIRef(f"{IMG}{row.image_id}")
        g.add((NS.Person1, REL.appearsIn, img))
        g.add((img, REL.hasScene, URIRef(f"{SCN}{row.scene}")))
        g.add((img, REL.hasFace, URIRef(f"{FACE}{row.faces}_{row.image_id}")))
        g.add((img, REL.hasLoc, Literal(row.location)))
        g.add((img, TIME.timestamp, Literal(date_str, datatype=XSD.date)))

    for row in df_calls[df_calls["date"] == date_str].itertuples():
        call = URIRef(f"{CALL}{row.call_id}")
        g.add((NS.Person1, REL.madeCall, call))
        g.add((call, REL.callWith, Literal(row.contact)))
        g.add((call, REL.durationMin, Literal(row.duration_min, datatype=XSD.integer)))
        g.add((call, REL.hasLoc, Literal(row.location)))
        g.add((call, TIME.timestamp, Literal(date_str, datatype=XSD.date)))

    for row in df_payments[df_payments["date"] == date_str].itertuples():
        pay = URIRef(f"{PAY}{row.Index}")
        g.add((NS.Person1, REL.madePayment, pay))
        g.add((pay, REL.amount, Literal(row.amount, datatype=XSD.integer)))
        g.add((pay, REL.merchant, Literal(row.merchant)))
        g.add((pay, REL.hasLoc, Literal(row.location)))
        g.add((pay, TIME.timestamp, Literal(date_str, datatype=XSD.date)))

    for row in df_location[df_location["date"] == date_str].itertuples():
        loc = URIRef(f"{LOC}{row.date}")
        g.add((NS.Person1, REL.wasAt, loc))
        g.add((loc, REL.lat, Literal(row.lat)))
        g.add((loc, REL.lon, Literal(row.lon)))
        g.add((loc, REL.city, Literal(row.city)))
        g.add((loc, TIME.timestamp, Literal(row.date, datatype=XSD.date)))

    return g

# Create TKGs for each day
tkg_by_day = {date: create_daily_tkg(date) for date in df_location["date"].tolist()}

# Show snapshot for Sept 5
sample_tkg = tkg_by_day["2024-09-05"].serialize(format="turtle")
sample_tkg.splitlines()[:30]
