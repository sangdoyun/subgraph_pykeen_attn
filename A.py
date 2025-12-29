
To clarify the "Identity" component of Temporal-Identity (TI) Gating, we must treat identity not as a label (e.g., "Me"), but as a persistent latent anchor that modulates how data flows through the system. This ensures that even if a user’s appearance evolves (e.g., aging or growing a beard), the model maintains a consistent "reasoning logic" tied to that specific person's history.
Here is how Identity is technically integrated into the PKG Knowledge Extraction and Manifold Projection blocks.
1. Block 1: TI-Gating in the GGNN (The Reasoning Filter)
The Challenge: In a 10-year KG, there may be many people with similar roles (e.g., "Boss," "Mentor," "Partner"). Without identity gating, a temporal search for "Coffee" might retrieve a 2018 memory of a boss's order instead of the user’s current preference.
 * Identity Anchoring: The "Gating Signal" carries a persistent Entity ID embedding (e_{id}). This is a unique, style-invariant vector retrieved from the KG that represents the person's core identity, decoupled from their current visual state.
 * The Technical Gate: In the GGNN, the Update Gate (\mathbf{z}_t) for a node is calculated by measuring the Identity Saliency:
   
 * The Role of Identity: The gate only "opens" for graph nodes that have a high semantic similarity to the specific Entity ID (e_{id}) in the current image. This prevents the model from mixing up preferences between different people who might appear in the same scene or have similar temporal history.
2. Block 2: Identity-Invariant Manifold Alignment
The Challenge: As a user ages or changes their appearance over 10 years (e.g., the "Identity Evolution" pain point), their raw visual tokens (V_{raw}) will naturally drift in the embedding space.
 * The Identity Manifold: The Constraint Manifold (\mathcal{M}) produced in Block 1 is centered around the Entity ID coordinate. It represents the "volume" of space where all facts about that specific person reside.
 * Projective Alignment (The "Identity Fix"): * When Block 2 receives raw pixels (V_{raw}) of a user with a new beard, the model calculates the Semantic Orthocy Score relative to the Entity ID manifold.
   * Technicality: The alignment layer performs a non-linear projection that shifts the drifted visual embedding back toward the persistent Entity ID manifold.
   * Result: The vision tokens are "forced" to represent the person's persistent identity rather than their current appearance. This is why the method is "Identity-Coupled"—the pixels are physically constrained by the KG's identity definition.
Example: Identity Persistence through Evolution
 * Input: User (now with a beard) holding red wine at a dinner.
 * Block 1 (TI-Gating): The GGNN extracts the user's persistent Entity ID. It gates out "Young User" visual nodes but gates in "User's Wine Preference" nodes because the Identity Saliency matches, even if the time and visual state differ.
 * Block 2 (Alignment): The vision encoder sees a "Bearded Man." The Manifold Alignment recognizes that this visual entity occupies the same relational space as the Entity ID for "User" in the KG. It projects the "Bearded Man" tokens into the "User" manifold.
 * Block 3 (Reasoning): Because the identity is now correctly "pinned" to the user's history, the Abductive Cformer can correctly infer: "The user is holding wine, but according to the Entity ID manifold, they dislike wine—therefore, this must be the gift for Sarah mentioned in their calendar."
Summary of the Technical Novelty
Standard models use Visual Similarity (Do they look like the same person?). We use Latent Relational Constancy via TI-Gating (Do they occupy the same logical space in the user's 10-year life graph?). This shift from "pixels" to "graph-centered identity" is the core contribution for an ICML-level paper.
Would you like me to formalize this Identity-ID projection as a specific mathematical objective function (loss function) for the paper?
