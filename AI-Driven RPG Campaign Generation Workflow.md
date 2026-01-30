# **Computational Architectures for Infinite Narrative: A Hierarchical Framework for AI-Driven RPG Campaign Generation**

## **1\. Executive Summary: The Transition from Static to Living Narratives**

The domain of interactive storytelling stands at a critical inflection point, driven by the convergence of Large Language Models (LLMs), symbolic planning algorithms, and procedural content generation (PCG). Historically, Role-Playing Games (RPGs) were constrained by the finite capacity of human authors to anticipate player agency. Traditional "Game Master" (GM) software functioned as static repositories of pre-written logic, unable to adapt to the chaotic, emergent nature of tabletop play where a single player decision can invalidate an entire narrative arc. The advent of generative AI promises an "Infinite Dungeon Master"—a system capable of synthesizing coherent, emotionally resonant, and mechanically rigorous campaigns in real-time. However, a significant gap remains between the generative capability of an LLM and the structural requirements of a game. "End-to-End" (E2E) generation, where a model is simply prompted to "write a campaign," inevitably succumbs to context drift, logical hallucinations, and narrative incoherence over long horizons.1

To bridge this gap, this report proposes and details a comprehensive **Hierarchical Generative Framework**. This architecture abandons the flat generation model in favor of a "Macro-Meso-Micro" stratified approach, mimicking human cognitive processes. It utilizes **Macro-Level** agents for strategic world simulation and campaign outlining, **Meso-Level** agents for structural episode and quest planning, and **Micro-Level** agents for the immediate, sensory-rich execution of session details. Crucially, this framework integrates **Neuro-Symbolic** methodologies: while LLMs provide the narrative flesh, the skeleton is maintained by rigid data structures—Directed Acyclic Graphs (DAGs), JSON Schemas, and Knowledge Graphs—ensuring that the "living story" remains logically sound and mechanically balanced.4

This document provides an exhaustive technical analysis of this framework, detailing the requisite data schemas, agentic workflows (leveraging LangGraph and CrewAI), and procedural asset pipelines required to build a system that acts not just as a storyteller, but as a coherent, omniscient, and reactive Game Master.

## **2\. Theoretical Foundations: The Cognitive Architecture of a Machine GM**

The fundamental challenge in AI-driven RPG generation is the tension between **Narrative Coherence** (adherence to a plot) and **Player Agency** (the freedom to deviate). A purely neural approach (LLM-only) excels at improvisation but fails at long-term consistency. A purely symbolic approach (GOFAI planners) excels at consistency but fails at improvisation. The proposed solution is a hybrid **Plan-and-Write** architecture that operationalizes the concept of **Recursive Reprompting and Revision (Re3)** within a hierarchical state machine.7

### **2.1 The Necessity of Hierarchical Planning**

Research into long-form story generation indicates that LLMs struggle with "forgetting" high-level goals as the token count increases. The "attention mechanism" in Transformer architectures, while powerful, dilutes the influence of initial prompts over thousands of turns.2 To counteract this, the narrative must be decomposed into "Abstract Acts" or skeletons.

The **Coarse-to-Fine (C2F)** generation paradigm posits that a narrative system must first generate a low-resolution outline (the Macro-plot) before attempting high-resolution rendering (the Session). This allows the system to validate the logical flow of the campaign *before* committing resources to text generation. If the Macro-plan is flawed (e.g., "The villain is defeated in Act 1 but appears in Act 3"), it can be detected and repaired at the symbolic level without needing to rewrite thousands of words of prose.10

### **2.2 The Recursive Reprompting (Re3) Framework**

The Re3 framework operationalizes the editorial process. In a tabletop RPG context, the "First Draft" is the AI's initial improvisation in response to a player action. However, this draft must be subjected to a **Critic/Reviewer Loop** before being presented to the player.

1. **Plan**: The system retrieves the current World State and Campaign Goal.  
2. **Draft**: The Writer Agent generates a response.  
3. **Review**: A Rules Lawyer Agent and a Lore Keeper Agent analyze the draft. Does it contradict the rulebook? Does it contradict the fact that the NPC died three sessions ago?  
4. **Revise**: If the review fails, the Writer Agent is "reprompted" with specific constraints (e.g., "Regenerate, but remember the NPC is dead").7

This recursive cycle creates a "Self-Correcting" narrative engine that maintains the illusion of a coherent reality, essential for the suspension of disbelief in RPGs.13

### **2.3 Graph Theory in Narrative Structure**

Narratives in this framework are not linear strings of text but **Directed Acyclic Graphs (DAGs)**.

* **Nodes** represent narrative states (scenes, encounters, decision points).  
* **Edges** represent transitions driven by player choice or mechanic triggers.  
* **Acyclicity** ensures the story moves forward in time, though "Loops" can be simulated via recursive sub-graphs (e.g., a time-loop puzzle). This graph-based approach allows for **Branching Plot Trees**, where the "State of the World" is determined by the path traversed through the graph. It also facilitates **Dynamic Replanning**: if a player breaks the graph (e.g., kills a critical quest giver), the system can calculate a new path through the remaining nodes or generate new nodes to bridge the gap, treating the narrative as a routing problem.14

## **3\. Macro-Architecture: The World Engine and Campaign Skeleton**

The Macro-Level is the strategic layer of the framework. It does not concern itself with the specific dialogue of a tavern keeper but rather the geopolitical movements of nations, the progression of villainous plots, and the overarching thematic tone. It functions as the "Campaign Bible."

### **3.1 The Knowledge Graph (KG) as World State**

To maintain a consistent "World Truth" over hundreds of sessions, the system cannot rely solely on the LLM's context window. Instead, it utilizes a **Knowledge Graph (KG)**—implemented via graph databases like Neo4j or lightweight network libraries—to store the relational data of the world.5

**Key Graph Entities and Relations:**

* **Entities (Nodes)**: NPCs, Factions, Locations, Artifacts, Concepts (e.g., "The Prophecy").  
* **Relations (Edges)**:  
  * NPC\_A \--\> Faction\_X  
  * Faction\_X \--\> Faction\_Y  
  * Location\_1 \--\> Artifact\_Z  
  * Event\_Alpha \--\> Event\_Beta

This structure allows for **Semantic Querying**. When a player asks, "Who is the enemy of my friend?", the system traverses the graph: Player \-\> Friend\_Node \-\> Enemy\_Edge \-\> Target\_Node. This is far more reliable than asking an LLM to "remember" relationships from session 1\.16

### **3.2 The Campaign Skeleton Schema**

The Campaign Skeleton is a structured JSON object that defines the high-level trajectory of the game. It uses a **Skeleton-Based Model** to define "Keyframes" or "Anchors"—events that *must* happen for the narrative arc to resolve—while leaving the "In-Between" space flexible for player agency.8

**Table 1: Macro-Level Campaign Data Schema**

| Field | Data Type | Description | Utility in Generation |
| :---- | :---- | :---- | :---- |
| campaign\_uuid | UUID | Unique identifier | Database indexing and retrieval |
| theme\_vectors | List | e.g., \["Cosmic Horror", "Noir", "Low Magic"\] | Conditions the tone of all Micro-generation (lexical choice) |
| global\_flags | Dict | {"king\_dead": true, "plague\_level": 4} | Conditional logic for quest availability |
| factions | List\[Object\] | Dynamic roster of power groups | Tracks reputation and off-screen faction moves |
| macro\_arc | DAG (JSON) | High-level abstract acts (e.g., "Act 1: Discovery") | Guides the Director Agent in long-term planning |
| active\_villains | List\[Object\] | Antagonists with independent goals | Drivers of "Fronts" or "Clocks" (Apocalypse World mechanics) |

### **3.3 Dynamic Replanning and "Living" Factions**

A static plot is fragile. The Macro-Architecture employs a **Multi-Agent Simulation** for off-screen events. Between sessions, a "World Sim" agent iterates through the Factions list. Based on the global\_flags and player actions, it advances the goals of the factions.

* *Example*: The players ignored the Cult of the Worm to save the Blacksmith. The World Sim updates the Cult's progress: Cult\_Ritual\_Progress \+= 1\.  
* *Consequence*: The Macro-plan is updated. The "Midpoint Climax" node is altered from "Disrupt the Ritual" to "Survive the Summoned Demon," reflecting the player's neglect. This creates a responsive, living world rather than a static railroad.18

## **4\. Meso-Architecture: Granular Episodes and Quest Trees**

The Meso-Level bridges the gap between the abstract campaign goals and the immediate gameplay session. It is responsible for **Quest Generation**, **Episode Structuring**, and **Branching Logic**. It translates "The Cult is rising" (Macro) into "Investigate the Crypt of Damp Sorrows" (Meso).

### **4.1 The Quest Definition Language (QDL)**

To standardize content, we define a **Quest Definition Language (QDL)** using JSON Schema. This allows the system to procedurally generate adventures that follow accepted game design patterns (e.g., The "Five Room Dungeon" or "The Hero's Journey").20

**Table 2: Quest Node Taxonomy in QDL**

| Node Type | Function | Required Assets | Failure State |
| :---- | :---- | :---- | :---- |
| **Hook** | Inciting incident | Rumor text, Quest Giver NPC | Player ignores hook (Replanning trigger) |
| **Gauntlet** | Combat/Resource drain | Encounter Map, Enemy Stat Blocks | Party death or retreat |
| **Puzzle** | Intellectual challenge | Riddle text, DC checks, Clue hierarchy | Puzzle unsolved (Gate closed) |
| **Roleplay** | Social interaction | NPC Profile, Dialogue Tree, Secret Knowledge | Diplomatic failure (Combat trigger) |
| **Reward** | Climax/Payout | Loot Table, XP Value, Lore Reveal | N/A |

### **4.2 Branching Narrative Structures**

The Meso-Level represents an adventure as a subgraph. Unlike the Macro-graph (which tracks years), the Meso-graph tracks days or hours. It uses **Hub-and-Spoke** topology for sandboxes:

* **Hub**: The "Safe Zone" (Town). Persistent state.  
* **Spoke**: The "Adventure Site." Generated JIT (Just-In-Time) when the player accepts the hook.  
* **Node Internal Logic**: Each node in the Meso-graph contains a mini-state machine.  
  * *Entrance Condition*: Has\_Key OR Lockpick\_Skill \> 15\.  
  * *Transition Logic*: IF Victory \-\> GoTo Node\_Treasure; IF Flee \-\> GoTo Node\_Wilderness.

This structure supports **Nested Plot Points**. A single node in the Macro-graph ("Investigate Cult") expands into an entire Meso-graph (The 5-Room Cult Dungeon). This "Zoom-In" capability is critical for managing LLM context; the LLM only needs to "see" the current Meso-graph, not the entire campaign history.22

### **4.3 Pre-Generated Asset Integration**

The prompt requires "pre-generated assets." At the Meso-level, this means the system generates the *entire* dungeon structure and its contents *before* the session begins.

* **Asset Bundling**: When a Meso-graph is generated, the system triggers the **Asset Pipeline** (detailed in Section 6). It generates the maps, the monster stats, and the loot tables for *all* nodes in the graph.  
* **Benefit**: This eliminates generation latency during the session. When players enter Room 3, the description and map are already cached, allowing for instant response times.18

## **5\. Micro-Architecture: Session-Level Execution and Mechanics**

The Micro-Level is the user interface of the narrative. It handles the "Theatre of the Mind," the parsing of player intent, and the adjudication of rules (e.g., D\&D 5e mechanics). It operates in a tight, real-time loop.

### **5.1 Sensory Description and "Read-Aloud" Generation**

The **Narrator Agent** generates the prose. To ensure quality, it utilizes **Prompt Templates** that enforce specific stylistic constraints.23

* **Prompt Structure**: \[Persona: Grimdark Fantasy Author\]\[Constraint: Max 150 words\].  
* **Output Separation**: The output schema separates "Public" (Read-Aloud) text from "Private" (DM Only) text.  
  * *Public*: "The air is frigid. A sarcophagus dominates the room."  
  * *Private*: "The sarcophagus is trapped. DC 15 Perception to spot the pressure plate."

### **5.2 Neuro-Symbolic Stat Block Generation**

Generating game statistics is a major weakness of pure LLMs (which often fail at basic arithmetic). The Micro-Architecture uses a **Constraint Satisfaction** approach.25

1. **Intent**: The Writer requests "A scary level 3 undead boss."  
2. **Retrieval (RAG)**: The system queries a vector database of the System Reference Document (SRD) for "Undead CR 3."  
3. **Template Filling**: It retrieves a template (e.g., "Wight") and uses the LLM to *flavor* the description ("Rotting King") while keeping the *numbers* (HP, AC, Attack Bonus) anchored to the balanced template.  
4. **Validation**: A **Rules Lawyer Agent** (Python script) validates the JSON: Check: Hit\_Dice\_Average \== HP. If the math is wrong, it autocorrects it before serving the asset.27

### **5.3 Real-Time Context Management**

The Micro-session manages the **Working Memory**.

* **Sliding Window**: It retains the last 10-20 turns of dialogue verbatim.  
* **Entity Injection**: It dynamically injects the JSON data of the *current* room and *active* NPCs into the system prompt.  
* **State Tracking**: It tracks immediate resource expenditure. Player\_HP, Spell\_Slots, Consumables. These are updated in the JSON state after every turn.29

## **6\. Procedural Asset Pipeline: From Text to Artifacts**

A robust RPG campaign requires more than text; it requires visual and mechanical artifacts. The framework incorporates a specialized pipeline for generating these assets from narrative descriptions.

### **6.1 Text-to-Map Generation Pipeline**

Visualizing the dungeon layout is critical for tactical RPGs. The pipeline integrates LLMs with procedural generation algorithms.30

1. **Semantic Parsing**: The LLM analyzes the Meso-graph node: "A flooded cavern with a central island and a narrow bridge."  
2. **Parameter Extraction**: It converts this into a JSON parameter file for a map generator:  
   JSON  
   {  
     "biome": "cavern",  
     "water\_level": 0.4,  
     "features": \["island", "bridge"\],  
     "grid\_size": \[20, 20\]  
   }

3. **Algorithmic Generation**: A Python script utilizing **Cellular Automata** (for organic caves) or **Binary Space Partitioning** (for built rooms) executes the generation. Libraries like networkx define the connectivity, while tile-set mappers render the visuals.33  
4. **Watabou Integration**: For higher-fidelity "sketched" maps, the system can interface with APIs for tools like Watabou's One Page Dungeon, parsing the returned SVG/JSON to identify wall colliders and door locations for VTT import.21

### **6.2 Image Generation Consistency**

For NPC portraits and scene backgrounds, the system uses diffusion models (e.g., Stable Diffusion). To maintain consistency (e.g., the same NPC looking the same across multiple images), the system uses **LoRA (Low-Rank Adaptation)** or **ControlNet** techniques. The Macro-level "Theme" defines the base prompt style, ensuring a unified aesthetic across the campaign.36

## **7\. Agentic Orchestration: The Multi-Agent System (MAS)**

Implementing this three-layer hierarchy requires a sophisticated orchestration engine. A single agent cannot effectively context-switch between "Creative Writer" and "Strict Rules Arbiter." We employ a **Multi-Agent System**.37

### **7.1 Framework Selection: LangGraph vs. AutoGen vs. CrewAI**

For this specific application, **LangGraph** is identified as the optimal orchestration framework due to its support for stateful, cyclic graphs and fine-grained control over execution flow, which maps perfectly to the RPG game loop.39

**Table 3: Comparative Analysis of Agent Frameworks for RPG Generation**

| Feature | LangGraph | AutoGen | CrewAI | Suitability for RPG |
| :---- | :---- | :---- | :---- | :---- |
| **Control Flow** | Explicit Graph (DAG/Cyclic) | Conversational | Process/Task-based | **LangGraph**: Best for rigid game loops and state machines. |
| **State Management** | Persistent State Object | Context Window | Task Context | **LangGraph**: Superior for tracking HP, Inventory, World Flags. |
| **Human-in-the-Loop** | Native Interrupts | via UserProxy | via Human Input | **LangGraph**: Allows the human GM to approve/edit generations. |
| **Code Execution** | Via Tool Nodes | Native Docker | Via Tools | **AutoGen**: Stronger for code generation, but overkill for narrative. |

### **7.2 The Agent Roster and Roles**

The architecture divides responsibilities among specialized agents, each with a distinct system prompt and toolset.41

1. **The Director (Orchestrator)**:  
   * *Role*: Managing the Macro/Meso state. Decides *what* happens next.  
   * *Tools*: Knowledge Graph Query, Replanning Algorithm.  
   * *Behavior*: Low creativity, high logic.  
2. **The Writer (Narrative)**:  
   * *Role*: Generating Micro-level prose.  
   * *Tools*: Style Guidelines, Thesaurus.  
   * *Behavior*: High creativity (Temperature 0.7+).  
3. **The Rules Lawyer (Mechanics)**:  
   * *Role*: Generating stats, resolving combat actions.  
   * *Tools*: SRD Database (RAG), Dice Roller, Python Math.  
   * *Behavior*: Deterministic (Temperature 0).  
4. **The Archivist (Memory)**:  
   * *Role*: Summarizing sessions, updating the vector DB.  
   * *Tools*: Vector DB (Upsert/Query), Summarizer.  
5. **The Cartographer (Asset)**:  
   * *Role*: Bridging text descriptions to map generation scripts.

### **7.3 Workflow Execution: The "Game Loop"**

The LangGraph workflow operates as a persistent state machine.

* **Step 1 (Router)**: User input is analyzed. Is it a meta-question ("Who is that?") or an action ("I attack")?  
* **Step 2 (Director)**: If action, check validity against World State. Determine consequence.  
* **Step 3 (Writer/Rules)**: Parallel execution. Writer drafts the description; Rules Lawyer calculates the damage/DC.  
* **Step 4 (Synthesizer)**: Merge text and mechanics. "You hit (Writer). 15 Damage (Rules)."  
* **Step 5 (Archivist)**: Asynchronous background update of the session log.43

## **8\. Memory & State Persistence: The MemGPT Approach**

Managing memory over a campaign that might span months of real-time is the "Context Window Problem." We implement a **Tiered Memory Architecture** inspired by **MemGPT**, effectively giving the AI an Operating System for memory.44

### **8.1 The Three Tiers of RPG Memory**

1. **Core Memory (The "BIOS")**:  
   * *Content*: The Agent's Persona, the absolute Core Truths of the setting (e.g., "Magic is illegal"), and the immediate Party Composition.  
   * *Storage*: System Prompt (Pinned context).  
   * *Update Frequency*: Rare (only major campaign shifts).  
2. **Recall Memory (The "Hard Drive")**:  
   * *Content*: Summaries of past sessions, NPC biographies, Lore entries, completed Quests.  
   * *Storage*: **Vector Database** (e.g., ChromaDB, Pinecone).  
   * *Mechanism*: **Retrieval Augmented Generation (RAG)**. When the player mentions "The Red Sword," the system embeds the query and retrieves the relevant lore chunk to inject into the context.2  
3. **Archival Memory (The "Logs")**:  
   * *Content*: Raw transcripts of every session, verbatim.  
   * *Storage*: Flat files or SQL Database.  
   * *Utility*: Used for "Deep Search" or re-summarization if the Recall Memory proves insufficient.22

### **8.2 The "Summary-Compress-Store" Cycle**

To prevent the Working Context (the immediate conversation) from overflowing, the **Archivist Agent** performs a cleanup routine at the end of every "Scene" or "Session".47

1. **Ingest**: Take the last \~2000 tokens of chat.  
2. **Summarize**: Convert to a concise narrative summary (e.g., "The party negotiated with the guard and paid a 50gp bribe.").  
3. **Entity Extraction**: Identify updates (Guard status: Bribed; Gold: \-50).  
4. **Update**: Write updates to the Campaign JSON and embed the summary into the Vector DB.  
5. **Flush**: Clear the working context, retaining only the summary and the new state.47

## **9\. Data Layer: Schema Specifications for Interoperability**

The success of this framework relies on rigorous data structuring. JSON Schemas act as the contract between the disparate agents, ensuring that the "Rules Lawyer" output is readable by the "Director."

### **9.1 The Master Campaign Schema**

This JSON object is the "Save File" of the entire campaign.

JSON

{  
  "meta": {  
    "campaign\_id": "uuid-v4",  
    "system": "D\&D 5e",  
    "created\_at": "timestamp",  
    "total\_sessions": 12  
  },  
  "macro\_state": {  
    "current\_act": 2,  
    "tension\_level": 4,  
    "world\_flags": {  
      "war\_declared": true,  
      "ancient\_seal\_broken": false  
    }  
  },  
  "roster":,  
  "quest\_log": {  
    "active": \["quest\_05\_find\_relic"\],  
    "completed": \["quest\_01", "quest\_02"\],  
    "failed": \["quest\_03\_save\_hostage"\]  
  },  
  "current\_context": {  
    "location\_id": "loc\_dungeon\_level\_2",  
    "meso\_graph\_ref": "graph\_dungeon\_01.json"  
  }  
}

### **9.2 The "Living" NPC Schema**

NPCs are not static text blocks; they are state objects tracked by the graph.28

JSON

{  
  "npc\_id": "npc\_blacksmith\_01",  
  "name": "Garrick",  
  "role": "Merchant",  
  "location": "Town\_Square",  
  "disposition": {  
    "base": "Neutral",  
    "current": "Friendly",  
    "modifiers": \[  
      {"source": "quest\_01\_success", "val": \+20},  
      {"source": "species\_bias\_dwarf", "val": \+5}  
    \]  
  },  
  "memory\_fragments":,  
  "stats": { "ref": "commoner\_stats" }  
}

## **10\. Operational Dynamics and Implementation Strategy**

### **10.1 Handling "Murder Hobos" and Narrative Deviation**

A critical requirement for any AI GM is handling players who violently deviate from the plot (the "Murder Hobo" phenomenon). The framework handles this via the **Consequence Engine** (part of the Director Agent).50

* **Detection**: The Rules Lawyer detects an attack on a "Essential" NPC.  
* **Warning**: The Micro-layer generates an in-game warning (e.g., "The guards look heavily armed").  
* **Execution**: If the player proceeds, the Director updates the Faction State (Town\_Guard: Hostile).  
* **Replanning**: The Macro-agent triggers a "Fail State" for the current quest and generates a new "Escape/Survival" quest. The story continues, but the genre shifts from "Heroic" to "Outlaw." The AI does *not* block the action, but simulates the logical consequences.52

### **10.2 Technical Stack Recommendations**

* **Core Logic**: Python (due to rich ecosystem for AI and Data).  
* **Orchestrator**: LangGraph (for stateful DAGs).  
* **LLM Backend**: Hybrid. GPT-4o or Claude 3.5 Sonnet for Director/Writer (high reasoning); GPT-4o-mini or Llama-3-8b for Rules Lawyer/Archivist (speed/cost).  
* **Database**: Neo4j (World Graph) \+ ChromaDB (Vector Memory) \+ Redis (Session State).  
* **Frontend**: Discord Bot interface (for accessibility) or dedicated React Web App (for displaying maps and character sheets).53

## **11\. Conclusion**

The hierarchical framework presented here—moving from Macro-World Simulation to Meso-Structural Planning to Micro-Sensory Execution—offers a robust solution to the limitations of current AI storytelling. By anchoring the generative power of LLMs within the rigid logic of Knowledge Graphs and Quest DAGs, we can create an RPG campaign generator that is not only infinite in scope but coherent in structure. This "Neuro-Symbolic" architecture ensures that player agency is respected without sacrificing narrative integrity, paving the way for the next generation of truly immersive, AI-driven role-playing experiences. The "Infinite Dungeon Master" is no longer a theoretical abstraction, but a tangible architectural reality.

#### **Works cited**

1. Beyond Outlining: Heterogeneous Recursive Planning for Adaptive Long-form Writing with Language Models \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2503.08275v3](https://arxiv.org/html/2503.08275v3)  
2. Generating Long-form Story Using Dynamic Hierarchical Outlining with Memory-Enhancement \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2412.13575v1](https://arxiv.org/html/2412.13575v1)  
3. Learning to Reason for Long-Form Story Generation \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2503.22828v1](https://arxiv.org/html/2503.22828v1)  
4. StoryVerse: Towards Co-authoring Dynamic Plot with LLM-based Character Simulation via Narrative Planning \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2405.13042v1](https://arxiv.org/html/2405.13042v1)  
5. Structured Graph Representations for Visual Narrative Reasoning: A Hierarchical Framework for Comics \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2506.10008v1](https://arxiv.org/html/2506.10008v1)  
6. Self-Correcting Adaptive Planning of Large Language Model on Knowledge Graphs, accessed January 28, 2026, [https://openreview.net/forum?id=CwCUEr6wO5\&referrer=%5Bthe%20profile%20of%20Liyi%20Chen%5D(%2Fprofile%3Fid%3D\~Liyi\_Chen3)](https://openreview.net/forum?id=CwCUEr6wO5&referrer=%5Bthe+profile+of+Liyi+Chen%5D\(/profile?id%3D~Liyi_Chen3\))  
7. Re3: Generating Longer Stories With Recursive Reprompting and Revision, accessed January 28, 2026, [https://violetpeng.github.io/bibliography/yang2022re3/](https://violetpeng.github.io/bibliography/yang2022re3/)  
8. A Skeleton-Based Model for Promoting Coherence Among Sentences in Narrative Story Generation | Request PDF \- ResearchGate, accessed January 28, 2026, [https://www.researchgate.net/publication/334115184\_A\_Skeleton-Based\_Model\_for\_Promoting\_Coherence\_Among\_Sentences\_in\_Narrative\_Story\_Generation](https://www.researchgate.net/publication/334115184_A_Skeleton-Based_Model_for_Promoting_Coherence_Among_Sentences_in_Narrative_Story_Generation)  
9. Re3: Generating Longer Stories With Recursive Reprompting and Revision \- The Berkeley NLP Group, accessed January 28, 2026, [https://nlp.cs.berkeley.edu/pubs/Yang-Tian-Peng-Klein\_2022\_Re3\_paper.pdf](https://nlp.cs.berkeley.edu/pubs/Yang-Tian-Peng-Klein_2022_Re3_paper.pdf)  
10. Can LLMs Generate Good Stories? Insights and Challenges from a Narrative Planning Perspective \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2506.10161v1](https://arxiv.org/html/2506.10161v1)  
11. Fine-to-coarse entailment hierarchy construction for coarse-to-fine story generation \- Amazon Science, accessed January 28, 2026, [https://www.amazon.science/publications/fine-to-coarse-entailment-hierarchy-construction-for-coarse-to-fine-story-generation](https://www.amazon.science/publications/fine-to-coarse-entailment-hierarchy-construction-for-coarse-to-fine-story-generation)  
12. Recursive Prompting Appears to Yield Meaningful Results \- OpenAI Developer Community, accessed January 28, 2026, [https://community.openai.com/t/recursive-prompting-appears-to-yield-meaningful-results/1249962](https://community.openai.com/t/recursive-prompting-appears-to-yield-meaningful-results/1249962)  
13. Re3: Generating Longer Stories With Recursive Reprompting and Revision \- arXiv, accessed January 28, 2026, [https://arxiv.org/abs/2210.06774](https://arxiv.org/abs/2210.06774)  
14. DAG: Directed Acyclic Graphs in computer sciences | by Jérôme DIAZ \- Medium, accessed January 28, 2026, [https://medium.com/@jerome.o.diaz/directed-acyclic-graphs-in-computer-sciences-a23f736f9dfb](https://medium.com/@jerome.o.diaz/directed-acyclic-graphs-in-computer-sciences-a23f736f9dfb)  
15. what-if: Exploring Branching Narratives by Meta-Prompting Large Language Models \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2412.10582v3](https://arxiv.org/html/2412.10582v3)  
16. How to Implement Custom JSON Utility Procedures With Memgraph MAGE and Python., accessed January 28, 2026, [https://memgraph.com/blog/how-to-implement-custom-json-utility-procedures-with-memgraph-mage-and-python](https://memgraph.com/blog/how-to-implement-custom-json-utility-procedures-with-memgraph-mage-and-python)  
17. \[1808.06945\] A Skeleton-Based Model for Promoting Coherence Among Sentences in Narrative Story Generation \- arXiv, accessed January 28, 2026, [https://arxiv.org/abs/1808.06945](https://arxiv.org/abs/1808.06945)  
18. How I Built an LLM-Based Game from Scratch | Towards Data Science, accessed January 28, 2026, [https://towardsdatascience.com/how-i-built-an-llm-based-game-from-scratch-86ac55ec7a10/](https://towardsdatascience.com/how-i-built-an-llm-based-game-from-scratch-86ac55ec7a10/)  
19. Adaptive Narratives: Unique Experiences in Video Games \- Syntetica \> Blog | Article, accessed January 28, 2026, [https://syntetica.ai/blog/blog\_article/adaptive-narratives-unique-experiences-in-video-games](https://syntetica.ai/blog/blog_article/adaptive-narratives-unique-experiences-in-video-games)  
20. PCG Book Chapter: Constructive Generation Methods for Dungeons and Levels \- Antonios Liapis, accessed January 28, 2026, [https://antoniosliapis.com/articles/pcgbook\_dungeons.php](https://antoniosliapis.com/articles/pcgbook_dungeons.php)  
21. Watabou's Procgen Arcana: Dungeon, accessed January 28, 2026, [https://watabou.github.io/dungeon.html](https://watabou.github.io/dungeon.html)  
22. I built an AI Dungeon Master with infinite memory...Claude Code helped me finish it in just two months after a year of struggling. \- Reddit, accessed January 28, 2026, [https://www.reddit.com/r/ClaudeCode/comments/1m7wbgv/i\_built\_an\_ai\_dungeon\_master\_with\_infinite/](https://www.reddit.com/r/ClaudeCode/comments/1m7wbgv/i_built_an_ai_dungeon_master_with_infinite/)  
23. The secret to writing quality stories with LLMs : r/LocalLLaMA \- Reddit, accessed January 28, 2026, [https://www.reddit.com/r/LocalLLaMA/comments/18zqy4s/the\_secret\_to\_writing\_quality\_stories\_with\_llms/](https://www.reddit.com/r/LocalLLaMA/comments/18zqy4s/the_secret_to_writing_quality_stories_with_llms/)  
24. LLM for plot expanding : r/LocalLLaMA \- Reddit, accessed January 28, 2026, [https://www.reddit.com/r/LocalLLaMA/comments/1ayx82m/llm\_for\_plot\_expanding/](https://www.reddit.com/r/LocalLLaMA/comments/1ayx82m/llm_for_plot_expanding/)  
25. How to Write LitRPG Without Losing Your Mind: Using AI for Stats, Systems, and Quests, accessed January 28, 2026, [https://sudowrite.com/blog/how-to-write-litrpg-without-losing-your-mind-using-ai-for-stats-systems-and-quests/](https://sudowrite.com/blog/how-to-write-litrpg-without-losing-your-mind-using-ai-for-stats-systems-and-quests/)  
26. We've been played DnD using an LLM \- here's the DM prompt I've refined over time \- Reddit, accessed January 28, 2026, [https://www.reddit.com/r/DungeonsAndDragons/comments/1q4uq4x/weve\_been\_played\_dnd\_using\_an\_llm\_heres\_the\_dm/](https://www.reddit.com/r/DungeonsAndDragons/comments/1q4uq4x/weve_been_played_dnd_using_an_llm_heres_the_dm/)  
27. Does Reasoning Help LLM Agents Play Dungeons and Dragons? A Prompt Engineering Experiment \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2510.18112v1](https://arxiv.org/html/2510.18112v1)  
28. dnd5epy \- PyPI, accessed January 28, 2026, [https://pypi.org/project/dnd5epy/](https://pypi.org/project/dnd5epy/)  
29. The LLM as Game Master: A New Era for Text Adventures with Gemini-2.5-Flash \- Medium, accessed January 28, 2026, [https://medium.com/ai-simplified-in-plain-english/the-llm-as-game-master-a-new-era-for-text-adventures-with-gemini-2-5-flash-26b5b934fa14](https://medium.com/ai-simplified-in-plain-english/the-llm-as-game-master-a-new-era-for-text-adventures-with-gemini-2-5-flash-26b5b934fa14)  
30. Moonshine: Distilling Game Content Generators into Steerable Generative Models, accessed January 28, 2026, [https://ojs.aaai.org/index.php/AAAI/article/view/33571/35726](https://ojs.aaai.org/index.php/AAAI/article/view/33571/35726)  
31. AI Map Maker | Generate Fantasy Maps for DnD & More \- Getimg.ai, accessed January 28, 2026, [https://getimg.ai/use-cases/ai-dnd-map-maker](https://getimg.ai/use-cases/ai-dnd-map-maker)  
32. Dungeon generation — from simple to complex \- tiendil-org, accessed January 28, 2026, [https://tiendil.org/en/posts/dungeon-generation-from-simple-to-complex](https://tiendil.org/en/posts/dungeon-generation-from-simple-to-complex)  
33. ProcGen \- 0.2 \- Pygame, accessed January 28, 2026, [https://www.pygame.org/project-ProcGen-2883-4741.html](https://www.pygame.org/project-ProcGen-2883-4741.html)  
34. joyeusenoelle/simple-procgen: Python script to generate simple "dungeon maps" \- GitHub, accessed January 28, 2026, [https://github.com/joyeusenoelle/simple-procgen](https://github.com/joyeusenoelle/simple-procgen)  
35. Watabou One Page Dungeon Converter for Dungeondraft \- Reddit, accessed January 28, 2026, [https://www.reddit.com/r/dungeondraft/comments/mh9qta/watabou\_one\_page\_dungeon\_converter\_for/](https://www.reddit.com/r/dungeondraft/comments/mh9qta/watabou_one_page_dungeon_converter_for/)  
36. Does anyone have any recommended text to picture AI tools I could use as a GM for generating maps and battlemaps? \- Reddit, accessed January 28, 2026, [https://www.reddit.com/r/rpg/comments/1b4haff/does\_anyone\_have\_any\_recommended\_text\_to\_picture/](https://www.reddit.com/r/rpg/comments/1b4haff/does_anyone_have_any_recommended_text_to_picture/)  
37. LLMs for Multi-Agent Cooperation | Xueguang Lyu, accessed January 28, 2026, [https://xue-guang.com/post/llm-marl/](https://xue-guang.com/post/llm-marl/)  
38. Simplify Multi-Agent AI Orchestration with Microsoft AutoGen | by Annie Cushing | Medium, accessed January 28, 2026, [https://medium.com/@annie\_7775/simplify-multi-agent-ai-orchestration-with-microsoft-autogen-be126e284273](https://medium.com/@annie_7775/simplify-multi-agent-ai-orchestration-with-microsoft-autogen-be126e284273)  
39. LangGraph in Action: Building Custom AI Workflows | by stark \- Medium, accessed January 28, 2026, [https://medium.com/@shudongai/langgraph-in-action-building-custom-ai-workflows-168ed34aa9f8](https://medium.com/@shudongai/langgraph-in-action-building-custom-ai-workflows-168ed34aa9f8)  
40. Is LangGraph the best framework for building a persistent, multi-turn conversational AI?, accessed January 28, 2026, [https://www.reddit.com/r/LangChain/comments/1okh4x2/is\_langgraph\_the\_best\_framework\_for\_building\_a/](https://www.reddit.com/r/LangChain/comments/1okh4x2/is_langgraph_the_best_framework_for_building_a/)  
41. D\&D Game Master Agent with RAG \- Tasking AI, accessed January 28, 2026, [https://www.tasking.ai/examples/dnd-game-master-agent-with-rag](https://www.tasking.ai/examples/dnd-game-master-agent-with-rag)  
42. Static Vs. Agentic Game Master AI for Facilitating Solo Role-Playing Experiences \- arXiv, accessed January 28, 2026, [https://arxiv.org/html/2502.19519v2](https://arxiv.org/html/2502.19519v2)  
43. D\&D General \- A.I. D\&D Session Transcripts and Summaries Example \- EN World, accessed January 28, 2026, [https://www.enworld.org/threads/a-i-d-d-session-transcripts-and-summaries-example.707199/](https://www.enworld.org/threads/a-i-d-d-session-transcripts-and-summaries-example.707199/)  
44. MemGPT: Engineering Semantic Memory through Adaptive Retention and Context Summarization \- Information Matters, accessed January 28, 2026, [https://informationmatters.org/2025/10/memgpt-engineering-semantic-memory-through-adaptive-retention-and-context-summarization/](https://informationmatters.org/2025/10/memgpt-engineering-semantic-memory-through-adaptive-retention-and-context-summarization/)  
45. MemGPT: Unlocking Unlimited Memory for Conversational AI | by Tarek AbdELKhalek, accessed January 28, 2026, [https://medium.com/@tiro2000/memgpt-unlocking-unlimited-memory-for-conversational-ai-6932002ea8e5](https://medium.com/@tiro2000/memgpt-unlocking-unlimited-memory-for-conversational-ai-6932002ea8e5)  
46. Seeking Advice: Best LLM Model for Consistent Long-Form Storytelling with 8GB VRAM, accessed January 28, 2026, [https://www.reddit.com/r/LocalLLM/comments/16cgtaz/seeking\_advice\_best\_llm\_model\_for\_consistent/](https://www.reddit.com/r/LocalLLM/comments/16cgtaz/seeking_advice_best_llm_model_for_consistent/)  
47. Level Up Your D\&D Session Notes: Useful AI Prompts & Cleanup Scripts \- Medium, accessed January 28, 2026, [https://medium.com/@brandonharris\_12357/level-up-your-d-d-session-notes-useful-ai-prompts-cleanup-scripts-ca959de9a541](https://medium.com/@brandonharris_12357/level-up-your-d-d-session-notes-useful-ai-prompts-cleanup-scripts-ca959de9a541)  
48. Understanding Memory Management in LangGraph: A Practical Guide for GenAI Students, accessed January 28, 2026, [https://pub.towardsai.net/understanding-memory-management-in-langgraph-a-practical-guide-for-genai-students-b3642c9ea7e1](https://pub.towardsai.net/understanding-memory-management-in-langgraph-a-practical-guide-for-genai-students-b3642c9ea7e1)  
49. A 5e JSON Schema \- GitHub Pages, accessed January 28, 2026, [https://swimminschrage.github.io/5e-schema/](https://swimminschrage.github.io/5e-schema/)  
50. 9 DM TIPS TO HANDLE PROBLEM PLAYERS (MUST WATCH) | Dungeons & Dragons, accessed January 28, 2026, [https://www.youtube.com/watch?v=MLZh3EFuVxU](https://www.youtube.com/watch?v=MLZh3EFuVxU)  
51. How do you actually get the AI to hurt or kill player characters? : r/AIDungeon \- Reddit, accessed January 28, 2026, [https://www.reddit.com/r/AIDungeon/comments/1eoqg9t/how\_do\_you\_actually\_get\_the\_ai\_to\_hurt\_or\_kill/](https://www.reddit.com/r/AIDungeon/comments/1eoqg9t/how_do_you_actually_get_the_ai_to_hurt_or_kill/)  
52. Is there a way to make the AI give consequences or let the player fail? : r/AIDungeon, accessed January 28, 2026, [https://www.reddit.com/r/AIDungeon/comments/1ef5f92/is\_there\_a\_way\_to\_make\_the\_ai\_give\_consequences/](https://www.reddit.com/r/AIDungeon/comments/1ef5f92/is_there_a_way_to_make_the_ai_give_consequences/)  
53. I record our sessions and use AI to make a summary : r/DMAcademy \- Reddit, accessed January 28, 2026, [https://www.reddit.com/r/DMAcademy/comments/1jvej7n/i\_record\_our\_sessions\_and\_use\_ai\_to\_make\_a\_summary/](https://www.reddit.com/r/DMAcademy/comments/1jvej7n/i_record_our_sessions_and_use_ai_to_make_a_summary/)