Let’s pick two concrete modules and walk through them step-by-step, showing:

1️⃣ Where embeddings are used
2️⃣ How KG embeddings work in each step
3️⃣ Where manifold projection can help for mobile

We’ll use:

Module 1: Entity Linking

Module 2: Link Prediction / Missing Relation Inference


These are two of the most embedding-dependent modules.


---

Module 1 — Entity Linking

Goal

Map text mentions to the correct KG entity.

Example input:

"I had sushi with John yesterday."

Detected entities:

John
sushi

Possible KG nodes:

John_Smith
John_Doe
John_Williams


---

Step-by-step Pipeline

Step 1 — Candidate Entity Retrieval

From the KG index retrieve candidates.

Example:

John → {John_Smith, John_Doe, John_Williams}

This step usually uses:

string match
or
entity dictionary

No embeddings yet.


---

Step 2 — Context Encoding

Encode surrounding context.

Example sentence:

"I had sushi with John yesterday."

Embedding (via SLM):

context_vector ∈ R^768

Example:

context_vector = SLM(sentence)


---

Step 3 — Entity Embedding Lookup

Each KG entity has an embedding.

Example:

John_Smith → vector
John_Doe → vector
John_Williams → vector

Traditional approach:

TransE entity embeddings

Dimension example:

entity_vector ∈ R^200


---

Step 4 — Manifold Projection (Mobile Optimization)

Since SLM embeddings are large:

768 dimensions

Project them to a smaller manifold.

Example projection:

P: R^768 → R^64

Result:

context_vector_projected ∈ R^64
entity_vector_projected ∈ R^64

Methods:

PCA
autoencoder
learned projection

Purpose:

reduce memory
faster similarity search
lower energy


---

Step 5 — Similarity Scoring

Compute similarity:

score = cosine(context_vector, entity_vector)

Example:

similarity(context, John_Smith) = 0.92
similarity(context, John_Doe)   = 0.35

Select highest score.

Result:

John → John_Smith


---

Mobile Benefits of Manifold Projection

Without projection:

768-d vector similarity

With projection:

64-d vector similarity

Benefits:

12x less computation
12x less memory

Important for:

mobile CPU
battery usage


---

Module 2 — Link Prediction

Goal

Predict missing triples.

Example KG:

(User, visited, SushiPlace)
(User, met, John)

Missing relation:

(John, visited, SushiPlace) ?


---

Step-by-step Pipeline

Step 1 — Retrieve Entity Embeddings

Look up embeddings:

John → vector h
visited → vector r
SushiPlace → vector t

Example dimension:

200


---

Step 2 — Manifold Compression (Mobile)

Project embeddings.

R^200 → R^32

This step can be precomputed.

Result:

h' r' t'


---

Step 3 — Translation Scoring (TransE)

Compute score:

score = ||h + r - t||

Lower score → better triple.

Example:

||John + visited - SushiPlace|| = 0.18

Small distance → triple likely true.


---

Step 4 — Candidate Ranking

Compare against other entities.

Example:

score(John visited SushiPlace) = 0.18
score(John visited Cafe)       = 0.55
score(John visited Library)    = 1.10

Prediction:

John visited SushiPlace


---

Where Manifold Projection Helps

Projection reduces:

embedding dimension
vector operations
memory footprint

Example:

Dimension	Vector Ops

200	heavy
32	lightweight


Mobile benefit:

faster inference
less RAM
lower battery


---

Combined Mobile Pipeline

Putting both modules together:

User query
      ↓
NER
      ↓
Entity linking
      ↓
context embedding (SLM)
      ↓
manifold projection
      ↓
entity similarity search
      ↓
resolved entities
      ↓
link prediction
      ↓
TransE scoring
      ↓
answer


---

Where SLM + LoRA fits

SLM provides:

context embeddings
semantic understanding

LoRA provides:

personalization
user-specific knowledge

KG embeddings provide:

graph reasoning
link prediction

Manifold projection ensures:

mobile efficiency


---

Key Insight

In a mobile KG system, manifold projection can be inserted at two places:

1️⃣ SLM embedding compression

768 → 64

2️⃣ KG embedding compression

200 → 32

This keeps the system fast enough for mobile inference.


---

If you want, I can also show something very interesting for your architecture:

There is a new trend replacing TransE-style embeddings with hyperbolic manifolds which can represent hierarchies with very low dimensions (5–10) — potentially much better for mobile devices.