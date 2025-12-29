This architecture aims to solve critical challenges in personalized AI, specifically the failure of current models to perform "Preference Grounded" abductive reasoning (inferring why a user acts based on preferences) and maintaining "Identity-Constrained" personalization despite visual changes over time.
The significant novelty of this refined flow, versus standard Retrieval-Augmented Generation (RAG), is that it moves personalization from a simple text-append at the end to an active constraint applied throughout the visual perception and reasoning stages. It uses a geometric "Constraint Manifold" (\mathcal{M}) derived from the user's Knowledge Graph (PKG) to align visual features and penalize attention mechanisms that contradict established user facts, thereby preventing relational hallucinations.
Here is a breakdown of the roles and responsibilities of each block, illustrated with the example of a user holding a cup of coffee at 11 PM, where the goal is to understand they are drinking decaf for sleep.
Running Example Inputs
 * Input Image (V_{raw}): User holding a mug at 11 PM.
 * Query (Q): "What is user doing?".
 * PKG: Contains 10 years of data, including the fact: "User purchases Decaf Blend coffee and values sleep."
Block 1: PKG Knowledge Extraction
Role: To efficiently retrieve highly relevant, persistent context from a massive longitudinal PKG without overwhelming the system with irrelevant noise. It defines the geometric "boundaries of truth" for the specific user.
 * Sub-blocks & Actions:
   * Entity Extraction & Gating Signal: Detects "cup," "user," and the time "11 PM" in the inputs to create a signal that triggers specific parts of the graph.
   * Saliency Triggered Pruning & Temporal Identity Gating: Uses the signal to prune the 10-year data, ignoring irrelevant history (e.g., a 5-year-old daytime coffee habit) and focusing on nighttime beverage preferences.
   * Temporal GGNN with Gated Activation: Processes the pruned graph to extract the precise relationship: "User drinks decaf at night."
 * Example Outputs:
   * Personal Context Vector (C_{pers}): A latent vector summarizing "Nighttime decaf preference".
   * Constraint Manifold (\mathcal{M}): A geometric representation defining the boundaries of truth (e.g., a subspace where "drinking at 11 PM" aligns with "decaf" and contradicts "caffeine").
Block 2: Identity Invariant Manifold Projection
Role: To ensure visual perception is conditioned on persistent identity and user facts, rather than just raw pixels. This solves "Identity-Constrained" issues where visual changes (like lighting or aging) confuse generic models.
 * Sub-blocks & Actions:
   * Frozen ViT: Processes the image into generic raw visual tokens (V_{raw}).
   * Manifold Alignment: Projects these raw tokens onto the Constraint Manifold (\mathcal{M}). This mathematically adjusts the visual features to align with the user's established reality.
 * Example Action: The raw pixels of the cup are projected onto \mathcal{M}. Because \mathcal{M} defines nighttime drinking as "decaf," the visual features are adjusted to represent "a personalized decaf vessel" rather than just a generic mug.
 * Example Output: KG Constrained Visual Features (V'_{KG})—visual representations that are now invariant to superficial changes and aligned with KG facts.
Block 3: Abductive Cformer
Role: To perform the actual "abductive reasoning" (the why). It bridges the linguistic query with the visual evidence, using personal context to direct attention only to factually consistent features.
 * Sub-blocks & Actions:
   * Query Fusion MLP: Combines the generic query "What is user doing?" (Q) with the specific context "Nighttime decaf preference" (C_{pers}) to create a Context Seeded Query (Q_{seed}) (essentially, "Look for visual evidence of decaf drinking").
   * Manifold Constrained Cross-Attention (MCCA): The seeded query attends to the constrained visual features (V'_{KG}). Crucially, this attention is penalized by \mathcal{M}. If the model tries to attend to features suggesting "caffeine energy," the manifold increases the penalty, suppressing that interpretation. Attention is focused only on features aligning with "decaf".
 * Example Output: Personalized Visual Tokens (\mathcal{T}_{pers})—a highly compressed visual summary meaning "Evidence of user drinking decaf".
Block 4: Personalized Response Generation
Role: To generate the final natural language response. Because the input tokens are already deeply constrained by user facts, the frozen LLM is prevented from hallucinating incorrect relationships.
 * Sub-blocks & Actions:
   * Frozen LLM with Prompt Finetuning: Receives the original query (Q) and the fact-constrained visual tokens (\mathcal{T}_{pers}) as a prefix.
   * User Facts Grounded Reasoning: The LLM decodes the tokens. Since the visual information is already restricted to "decaf evidence," the LLM performs abductive reasoning based only on these facts.
 * Example Output: Personalized Abductive Answer: "The user is having their usual decaf blend for better sleep.".
