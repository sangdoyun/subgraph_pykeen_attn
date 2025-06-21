from rdflib import URIRef
import networkx as nx

def extract_graph_edges_for_centrality(graph):
    G = nx.DiGraph()
    for s, p, o in graph:
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            G.add_edge(str(s), str(o), predicate=str(p))
    return G

def find_centrality_anchors(graph, top_k=10):
    G_nx = extract_graph_edges_for_centrality(graph)
    centrality = nx.degree_centrality(G_nx)
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    return [node for node, score in sorted_nodes[:top_k]]

from collections import defaultdict

def find_path_based_anchors(graph, max_depth=3, min_freq=3):
    freq_count = defaultdict(int)
    
    def dfs(node, depth, visited):
        if depth > max_depth:
            return
        visited.add(node)
        freq_count[str(node)] += 1
        for _, _, neighbor in graph.triples((node, None, None)):
            if isinstance(neighbor, URIRef) and neighbor not in visited:
                dfs(neighbor, depth + 1, visited.copy())

    for s in set(graph.subjects()):
        if isinstance(s, URIRef):
            dfs(s, 0, set())

    # Select top nodes with freq above threshold
    path_anchors = [node for node, count in freq_count.items() if count >= min_freq]
    return path_anchors


# Centrality anchors
centrality_anchors = find_centrality_anchors(g, top_k=10)

# Path-based anchors
path_anchors = find_path_based_anchors(g, max_depth=3, min_freq=3)

# Combine all types
all_anchors = set(loc_uris) | set(centrality_anchors) | set(path_anchors)

def compute_centrality_graph(g_rdf):
    G_nx = nx.DiGraph()
    for s, p, o in g_rdf:
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            G_nx.add_edge(str(s), str(o), label=str(p))
    centrality = nx.degree_centrality(G_nx)
    return centrality
    
def detect_centrality_anchors(g_today, g_yesterday, threshold=0.2):
    c_today = compute_centrality_graph(g_today)
    c_yest = compute_centrality_graph(g_yesterday)

    anchors = []
    for node in c_today:
        delta = abs(c_today.get(node, 0) - c_yest.get(node, 0))
        if delta > threshold:
            anchors.append(node)
    return anchors

def find_frequent_path_nodes(graph_snapshots, path_len=3, freq_threshold=3):
    path_count = defaultdict(int)

    for g in graph_snapshots:
        G_nx = nx.DiGraph()
        for s, p, o in g:
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                G_nx.add_edge(str(s), str(o))

        for node in G_nx.nodes:
            for path in nx.single_source_simple_paths(G_nx, node, cutoff=path_len):
                for n in path:
                    path_count[n] += 1

    anchors = [node for node, count in path_count.items() if count >= freq_threshold]
    return anchors

from rdflib import Graph, URIRef, Namespace, RDF, Literal, XSD
from datetime import datetime
import networkx as nx
from pyvis.network import Network

EX = Namespace("http://example.org/")  # Replace with actual

# Load original RDF graph
g = Graph()
g.parse("reified_2_day_tkg_img.ttl", format="ttl")

# --- Utility ---
def extract_time(graph, event):
    for t in graph.objects(event, EX.hasTimestamp):
        if isinstance(t, Literal) and t.datatype == XSD.dateTime:
            return datetime.fromisoformat(str(t))
    return None

def score_node(graph, node):
    score = 0
    if (node, RDF.type, EX.Person) in graph: score += 3
    if (node, RDF.type, EX.Location) in graph: score += 2
    if (node, RDF.type, EX.Image) in graph: score += 1
    if (node, EX.hasTimestamp, None) in graph: score += 1
    return score

# --- Core extraction ---
def extract_rdf_subgraph(graph, anchor_uri, delta_t=1, k_hops=2, score_threshold=1):
    anchor_events = set(s for s, p, o in graph.triples((None, None, anchor_uri))).union(
        set(s for s, p, o in graph.triples((anchor_uri, None, None)))
    )
    anchor_times = [extract_time(graph, e) for e in anchor_events if extract_time(graph, e)]
    print (anchor_times)

    E_t = set()
    for e in graph.subjects(RDF.type, EX.Event):
        t = extract_time(graph, e)
        if t and any(abs((t - ta).days) <= delta_t for ta in anchor_times):
            E_t.add(e)

    E_prime = anchor_events.union(E_t)

    # Create new RDF subgraph
    subg = Graph()
    visited = set()
    frontier = set(E_prime)

    def add_related_triples(entity):
        for s, p, o in graph.triples((entity, None, None)):
            subg.add((s, p, o))
            if isinstance(o, URIRef):
                frontier.add(o)
        for s, p, o in graph.triples((None, None, entity)):
            subg.add((s, p, o))
            if isinstance(s, URIRef):
                frontier.add(s)

    for e in E_prime:
        add_related_triples(e)
        visited.add(e)

    for _ in range(k_hops):
        next_frontier = set()
        for node in frontier:
            if node in visited:
                continue
            if score_node(graph, node) >= score_threshold:
                add_related_triples(node)
                visited.add(node)
        frontier = next_frontier

    return subg
