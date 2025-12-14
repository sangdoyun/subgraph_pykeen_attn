This response is formatted as a single, comprehensive slide structure, suitable for presentation in A0 size using PowerPoint or similar software.

***

# ContextGraph: Lifelog Intelligence Framework for Contextual Subgraph Evolution

**Anil Sharma, Gunturi Venkata Sai Phani Kiran, Jayesh Rajkumar Vachhani, et al.** (AAAI 2026)

## 1. Introduction and Motivation

**The Challenge:** Smartphone lifelog data is fragmented, heterogeneous, and constantly flowing. Traditional lifelogging systems focus on simple data retrieval ("photos from the park") but **lack the ability to reason about behavioral evolution** (e.g., detecting gradual habit formation or emerging routines).

**Our Solution:** **ContextGraph** models lifelogs as an **evolving Temporal Knowledge Graph (TKG)** to track and explain changes in user behavior. We use **Day Context Embeddings (DCE)** for holistic daily representation and a **Lens Module** to track the evolution of specific life aspects (subgraphs).

| **Real-World Example (TKG Events)** |
| :--- |
| `7AM Home Wifi Connected` |
| `9AM Commute to work` |
| `5PM Payment for Groceries` |

---

## 2. Methodology: Modeling Context and Dynamics

### 2.1 TKG Construction and Daily Snapshots

Fragmented smartphone data (sensors, app usage, photos) is unified into an RDF-based TKG using reified quadruples $(s, p, o, \tau)$, where $\tau$ is the timestamp.

**Daily Snapshot ($G_d$):** Represents the user's semantic footprint on day $d$.
$$G_d = \{(s, p, o) | (s, p, o, \tau) \in G \wedge day(\tau) = d\} \text{}$$

### 2.2 Day Context Embeddings (DCE)

DCE uses a **dual Variational Autoencoder (VAE) architecture** to fuse temporal dynamics and contextual graph structure into a single latent vector ($z_d \in \mathbb{R}^{128}$).

> **FIGURE PLACEHOLDER:** DCE Architecture Diagram (Referencing Figure 3): Illustrate $G_d$ feeding into two VAE paths (Temporal-VAE and Context-GVAE) to produce the fused DCE.

| **DCE Component** | **Goal** | **Key Loss Function** |
| :--- | :--- | :--- |
| **Temporal-VAE** | Encodes the **temporal rhythm** (sequence, timing, duration) using Bi-directional LSTM. | $$L_{temporal} = E_{q(z|x)}[\log p(y|z)] - \beta \cdot D_{KL}(q(z|x)||p(z)) \text{}$$ |
| **Context-GVAE** | Encodes the **relational structure and semantics** (who, where, what) using Heterogeneous Graph Attention Networks (HAN). | $$L_{context} = L_{recon} + \beta \cdot D_{KL}(q(z|G_d)||p(z)) \text{}$$ |

---

## 3. The Lens Module: Tracking Behavioral Evolution

The Lens module identifies trigger points and tracks semantically meaningful subgraphs over time, enabling longitudinal reasoning.

> **FIGURE PLACEHOLDER:** Lens Architecture Pipeline (Referencing Figure 5/145): TKG $\rightarrow$ Anchor Detection $\rightarrow$ Subgraph Expansion $\rightarrow$ Dual-Similarity Analysis $\rightarrow$ Evolution Signature.

### 3.1 Volatile Anchor Detection
Anchor nodes ($v \in V_p$) are persistent entities flagged for selection if their DCE node embeddings show an abrupt change from the previous day, signaling a contextual shift (e.g., new payments, step spikes).
$$\text{Anchor Selection: } a_v(v) = \left\{v\middle| \frac{\| (e^d_v - e^{d-1}_v) \|_2}{\| (e^{d-1}_v) \|_2} > \tau_v \wedge v \in V_p\right\} \text{}$$

### 3.2 Context-Aware Subgraph Expansion
Subgraphs are expanded around the anchor based on a contextual **attention score ($\kappa$)**, prioritizing neighbors that are highly aligned with the anchor using DCE embeddings.
$$\text{Attention Score: } \kappa(a, p, o) = \cos(e_a + e_p, e_o) \text{}$$

### 3.3 Temporal Evolution Signature ($\epsilon$)
The evolution is tracked across snapshots using **Graph-level similarity ($M_G$)** (structure change) and **Node-level similarity ($M_N$)** (content change).

| **Evolution Signature $\epsilon$** | **Criteria** ($\theta_G=0.7, \theta_N=0.8$) | **Behavioral Insight** |
| :--- | :--- | :--- |
| **Static** | $M_G > \theta_G$ AND $M_N > \theta_N$ | Stable Routine/Habit |
| **Growing** | $M_G > \theta_G$ AND $M_N \le \theta_N$ | Routine structure stable, content expanding |
| **Decay** | $M_G \le \theta_G$ AND $M_N \le \theta_N$ | Habit Dropped/Routine Ending |

---

## 4. Results and Real-World Application

### 4.1 DCE Performance and Efficiency

| **Classification Performance (F1-score)** |
| :--- |
| DCE (Aggregate) consistently outperforms baselines on general graph classification (Enzyme, DBLP) and TPP-derived data. |

| Dataset | Node2Vec/DeepWalk | PELT (Frequency) | **DCE (Aggregate)** |
| :--- | :--- | :--- | :--- |
| OOD TPP-derived | 0.534 / 0.562 | 0.461 | **0.708** |
| DBLP (Macro-F1) | N/A | 0.30 | **0.89** |

| **Embedding Quality (Table 2 Summary)** |
| :--- |
| The fusion of temporal and context VAEs results in high **Inter-Class Distance** (**1.144**). DCE successfully separates activities with similar temporal dynamics (e.g., evening run vs. family event) by integrating contextual information. |
| **Runtime Advantage:** DCE reduces embedding computation time by **87.5%** (8 seconds vs. 100 seconds for Node2Vec/DeepWalk per graph). |

> **FIGURE PLACEHOLDER:** t-SNE Plot (Referencing Figure 6): Visualization showing DCE clusters clearly separated, unlike Temporal-VAE alone.

### 4.2 Real-World Case Study: Travel Detection

ContextGraph uses the Lens module on real smartphone lifelog data (Gallery images, POI metadata) to detect routine transitions like travel.

1.  **Trigger:** Lens identifies a volatile anchor (e.g., a new location node) by tracking low cosine similarity between daily node embeddings.
2.  **Reasoning:** The evolution signature provides the necessary context:
    *   A **decaying subgraph** around a previously active location suggests **Departure/Transition**.
    *   A **growing subgraph** around a new location indicates **Arrival/Prolonged Stay**.
3.  **Insight:** By analyzing this evolution, ContextGraph accurately confirms travel events and resolves duration issues. If the detected travel duration overlaps with the stay duration (based on subgraph evolution) by more than 0.75, the duration is reliably expanded.

> **FIGURE PLACEHOLDER:** Travel Detection Timeline (Referencing Figure in Section 6, Supp. Doc/Figure 7): Show an anchor detection (blue triangle) and the tracking of its associated growing/decaying subgraph over several days, confirming the accurate trip duration.

---

## 5. Conclusion and Future Work

**ContextGraph** successfully models multimodal lifelog data as TKGs, leveraging **DCE** for robust, holistic daily representations, and the **Lens module** for longitudinal reasoning. This enables intelligence beyond simple retrieval, providing **actionable insights** into behavioral drifts and lifestyle changes.

**Key Takeaway:** ContextGraph shifts lifelog systems from merely recording events to actively analyzing **evolving behaviors**.
