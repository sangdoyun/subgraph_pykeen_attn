from rdflib.namespace import RDF
from datetime import datetime
from collections import defaultdict

# 1. Extract all event triples with time
daily_events = defaultdict(list)

for stmt in g.subjects(predicate=RDF.type, object=RDF.Statement):
    timestamp = g.value(stmt, time.hasTimestamp)
    if timestamp:
        dt = datetime.fromisoformat(str(timestamp))
        day_key = dt.date().isoformat()
        daily_events[day_key].append(stmt)

daily_locations = {}

for day, stmts in daily_events.items():
    locations = set()
    for evt in stmts:
        subj = g.value(evt, RDF.subject)
        pred = g.value(evt, RDF.predicate)
        obj = g.value(evt, RDF.object)

        if pred == ex.appearsIn:
            loc = g.value(obj, ex.hasLocation)
            city = g.value(loc, geo.hasCity)
            country = g.value(loc, geo.hasCountry)
            locations.add((city, country))
    
    daily_locations[day] = locations

travel_sessions = []
prev_city = None
active_session = None

for day, locs in sorted(daily_locations.items()):
    cities = {c for c, _ in locs if c}
    
    # If location changed from previous day
    if not prev_city:
        prev_city = next(iter(cities), None)
        continue

    current_city = next(iter(cities), None)
    if current_city != prev_city:
        if not active_session:
            active_session = {"start": day, "from": prev_city, "to": current_city}
    else:
        if active_session:
            active_session["end"] = day
            travel_sessions.append(active_session)
            active_session = None
    prev_city = current_city

# Re-imports after execution environment reset
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from datetime import datetime
from collections import defaultdict

def extract_daily_snapshots_and_travel_sessions(g, person_uri, ex, geo, time_ns):
    """
    Extract daily snapshots and detect travel sessions from a temporal KG.
    
    Args:
        g: RDFLib Graph with reified events and location links.
        person_uri: URIRef of the person (e.g., ex.John).
        ex: Namespace for custom properties.
        geo: Namespace for location properties.
        time_ns: Namespace for time (e.g., time.hasTimestamp).
        
    Returns:
        travel_sessions: list of dicts with 'start', 'end', 'from', 'to'
        travel_subgraphs: list of RDFLib Graphs representing the travel subgraphs
    """
    daily_events = defaultdict(list)

    # Step 1: Group events by day
    for stmt in g.subjects(predicate=RDF.type, object=RDF.Statement):
        subj = g.value(stmt, RDF.subject)
        if subj != person_uri:
            continue
        pred = g.value(stmt, RDF.predicate)
        obj = g.value(stmt, RDF.object)
        timestamp = g.value(stmt, time_ns.hasTimestamp)
        if timestamp:
            dt = datetime.fromisoformat(str(timestamp))
            day_key = dt.date().isoformat()
            daily_events[day_key].append((stmt, subj, pred, obj, dt))

    # Step 2: Extract city for each day
    daily_locations = {}
    for day, entries in daily_events.items():
        cities = set()
        for _, _, pred, obj, _ in entries:
            if pred == ex.appearsIn:
                loc = g.value(obj, ex.hasLocation)
                city = g.value(loc, geo.hasCity)
                if city:
                    cities.add(str(city))
        daily_locations[day] = cities

    # Step 3: Detect travel sessions
    sorted_days = sorted(daily_locations.keys())
    travel_sessions = []
    travel_subgraphs = []

    prev_city = None
    active_session = None
    session_days = []

    for day in sorted_days:
        cities = daily_locations[day]
        city = next(iter(cities), None) if cities else None

        if not prev_city:
            prev_city = city
            continue

        if city != prev_city and city is not None:
            if not active_session:
                active_session = {"start": day, "from": prev_city, "to": city}
                session_days = [day]
        elif city == prev_city:
            if active_session:
                active_session["end"] = day
                travel_sessions.append(active_session)

                # Extract subgraph
                sg = Graph()
                for d in session_days:
                    for stmt, subj, pred, obj, dt in daily_events[d]:
                        sg.add((stmt, RDF.type, RDF.Statement))
                        sg.add((stmt, RDF.subject, subj))
                        sg.add((stmt, RDF.predicate, pred))
                        sg.add((stmt, RDF.object, obj))
                        sg.add((stmt, time_ns.hasTimestamp, Literal(dt.isoformat(), datatype=XSD.dateTime)))
                        sg.add((subj, pred, obj))  # Original triple (optional)
                        if pred == ex.appearsIn:
                            loc = g.value(obj, ex.hasLocation)
                            if loc:
                                for p, o in g.predicate_objects(loc):
                                    sg.add((loc, p, o))
                                sg.add((obj, ex.hasLocation, loc))
                travel_subgraphs.append(sg)

                # Reset
                active_session = None
                session_days = []
        else:
            if active_session:
                session_days.append(day)

        prev_city = city

    return travel_sessions, travel_subgraphs



from rdflib import Namespace, URIRef

# Define namespaces
ex = Namespace("http://example.org/")
geo = Namespace("http://example.org/geo/")
time = Namespace("http://example.org/time/")

# Your RDFLib graph
# g = your_loaded_graph
# person_uri = URIRef("http://example.org/John")

sessions, subgraphs = extract_daily_snapshots_and_travel_sessions(g, person_uri, ex, geo, time)

# Re-run necessary imports and regenerate TKG for Sept 5 after kernel reset
import pandas as pd
import random
from datetime import datetime, timedelta
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import XSD
from pyvis.network import Network

# Simulate date and city range again
date_range = [datetime(2024, 9, 1) + timedelta(days=i) for i in range(10)]
city_by_day = ["City1"]*4 + ["City2"]*4 + ["City1"]*2

# Containers
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

# Create DataFrames
df_images = pd.DataFrame(images_data)
df_calls = pd.DataFrame(calls_data)
df_location = pd.DataFrame(location_data)
df_payments = pd.DataFrame(payments_data)

# Namespaces
NS = Namespace("http://example.org/")
IMG = Namespace("http://example.org/image/")
CALL = Namespace("http://example.org/call/")
LOC = Namespace("http://example.org/location/")
PAY = Namespace("http://example.org/payment/")
TIME = Namespace("http://example.org/time/")
REL = Namespace("http://example.org/relation/")
SCN = Namespace("http://example.org/scene/")
FACE = Namespace("http://example.org/face/")

# Create graph for Sept 5
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

# Visualize with pyvis
def visualize_tkg_pyvis(graph, title="TKG Day View"):
    net = Network(height="500px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    net.force_atlas_2based()

    added_nodes = set()
    for s, p, o in graph:
        s_str, p_str, o_str = str(s), str(p).split("/")[-1], str(o)

        if s_str not in added_nodes:
            net.add_node(s_str, label=s_str.split("/")[-1], title=s_str, shape='ellipse')
            added_nodes.add(s_str)
        if o_str not in added_nodes:
            shape = 'box' if 'example.org/scene' in o_str or 'face' in o_str or o_str.startswith('"') else 'ellipse'
            net.add_node(o_str, label=o_str.split("/")[-1].strip('"'), title=o_str, shape=shape)
            added_nodes.add(o_str)

        net.add_edge(s_str, o_str, label=p_str)

    net.repulsion(node_distance=120, spring_length=200)
    return net

# Generate and show pyvis network
tkg_sept5 = create_daily_tkg("2024-09-03")
net_vis = visualize_tkg_pyvis(tkg_sept5)
net_vis.save_graph("tkg_sept3.html")

tkg_sept5 = create_daily_tkg("2024-09-04")
net_vis = visualize_tkg_pyvis(tkg_sept5)
net_vis.save_graph("tkg_sept4.html")

tkg_sept5 = create_daily_tkg("2024-09-03")
net_vis = visualize_tkg_pyvis(tkg_sept5)
net_vis.save_graph("tkg_sept3.html")

tkg_sept5 = create_daily_tkg("2024-09-06")
net_vis = visualize_tkg_pyvis(tkg_sept5)
net_vis.save_graph("tkg_sept6.html")


# Re-run necessary imports and regenerate data after reset
import pandas as pd
import random
from datetime import datetime, timedelta
from geopy.distance import geodesic
import uuid

# --- Regenerate simulated data ---
# Config
HOME_LOC = (28.6139, 77.2090)  # Delhi
CITY_POOL = {
    "Paris": (48.8566, 2.3522),
    "New York": (40.7128, -74.0060),
    "Tokyo": (35.6895, 139.6917),
    "Bangalore": (12.9716, 77.5946),
    "Goa": (15.2993, 74.1240),
}
SCENE_POOL = ["monument", "food", "beach", "street", "family", "selfie"]
FACES_POOL = [{"gender": g} for g in ["male", "female"]]

# Output storage
taking_pic = []
staying_act = []
travel_coll = []

# Helper
def random_time_span(start_date, min_hours=1, max_hours=3):
    start_time = start_date + timedelta(hours=random.randint(8, 18))
    duration = timedelta(hours=random.randint(min_hours, max_hours))
    return start_time, start_time + duration

def random_face_data(mode):
    count = random.randint(1, 2) if mode == "solo" else random.randint(2, 5)
    return [dict(id=str(uuid.uuid4())[:6], gender=random.choice(["male", "female"]), bbox=str((10,10,50,50))) for _ in range(count)]

# Generate data
start_date = datetime(2023, 1, 1)
days = 10  # short for demo
city_by_day = ["City1"] * 4 + ["Paris"] * 4 + ["City1"] * 2
dates = [start_date + timedelta(days=i) for i in range(days)]

images_data, calls_data, location_data, payments_data = [], [], [], []

for i, date in enumerate(dates):
    date_str = date.strftime('%Y-%m-%d')
    city = city_by_day[i]
    lat, lon = HOME_LOC if city == "City1" else CITY_POOL[city]

    for j in range(random.randint(1, 3 if city != "City1" else 1)):
        images_data.append({
            "date": date_str,
            "image_id": f"img_{i}_{j}",
            "scene": random.choice(SCENE_POOL),
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
        "lat": lat + random.uniform(-0.01, 0.01),
        "lon": lon + random.uniform(-0.01, 0.01),
        "city": city
    })

    for j in range(random.randint(1, 2 if city != "City1" else 1)):
        payments_data.append({
            "date": date_str,
            "merchant": random.choice(["Cafe", "Uber", "Museum", "Restaurant", "Store"]),
            "amount": random.randint(5, 50),
            "location": city
        })

# Create DataFrames
df_images = pd.DataFrame(images_data)
df_calls = pd.DataFrame(calls_data)
df_location = pd.DataFrame(location_data)
df_payments = pd.DataFrame(payments_data)

# Helper to get location
def get_location_for_day(date_str):
    row = df_location[df_location["date"] == date_str].iloc[0]
    return (row["lat"], row["lon"]), row["city"]

# Anchor + Subgraph logic
home_city = "City1"
location_threshold_km = 30
anchor_triggered = False
subgraph_days = []
subgraph_info = {}

dates_str = sorted(df_location["date"].unique())

for i in range(1, len(dates_str)):
    prev_date = dates_str[i - 1]
    curr_date = dates_str[i]

    loc_prev, city_prev = get_location_for_day(prev_date)
    loc_curr, city_curr = get_location_for_day(curr_date)

    distance_km = geodesic(loc_prev, loc_curr).km

    if not anchor_triggered and city_curr != home_city and distance_km > location_threshold_km:
        anchor_triggered = True
        subgraph_info = {"start": curr_date, "start_city": city_curr}
        subgraph_days = [curr_date]
    elif anchor_triggered and city_curr == home_city:
        anchor_triggered = False
        subgraph_info["end"] = curr_date
        subgraph_info["days"] = subgraph_days.copy()
        break
    elif anchor_triggered:
        subgraph_days.append(curr_date)

# Extract subgraph data
travel_images = df_images[df_images["date"].isin(subgraph_info["days"])]
travel_calls = df_calls[df_calls["date"].isin(subgraph_info["days"])]
travel_payments = df_payments[df_payments["date"].isin(subgraph_info["days"])]
travel_locations = df_location[df_location["date"].isin(subgraph_info["days"])]

# Summary
{
    "Travel Episode": subgraph_info,
    "Images": travel_images.shape[0],
    "Calls": travel_calls.shape[0],
    "Payments": travel_payments.shape[0],
    "Unique Cities": travel_locations["city"].unique().tolist()
}
