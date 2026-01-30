# **Integrating the Rulebook (SRD) via RAG**

You cannot hardcode every spell. Instead, you index the System Reference Document (SRD) into a Vector Database.

## **1\. The Data Pipeline (Ingestion)**

**Step A: Parsing the Rulebook**

Convert the 5e SRD (available as JSON/Markdown) into "Knowledge Chunks."

* **Bad Chunking:** Splitting by page number. (Breaks logic).  
* **Good Chunking:** Splitting by "Concept."  
  * *Chunk 1:* Spell: Fireball (Damage, Range, Components)  
  * *Chunk 2:* Condition: Prone (Effects on movement and attack)  
  * *Chunk 3:* Action: Grapple (Athletics vs Acrobatics)

**Step B: Vectorization**

Store these chunks in ChromaDB or Pinecone.

## **2\. The Retrieval Workflow (The "Slow Path")**

When a user tries something complex (not just "I swing sword"), we trigger the Librarian.

**Scenario:** Player says "I want to cast *Heat Metal* on the golem's armor."

1. **Intent Parser:** Detects cast\_spell intent. Extracts keywords: Heat Metal, Golem, Armor.  
2. **RAG Query:** The system searches the Vector DB for:  
   * "Spell: Heat Metal"  
   * "Monster: Golem (Immunities)"  
3. **Context Injection:** The system pastes the retrieved text into the LLM prompt.

**Generated Prompt for LLM:**

SYSTEM: You are a Rules Referee. Determine the outcome based ONLY on the provided rules.

USER ACTION: Cast 'Heat Metal' on Golem's armor.

RETRIEVED RULE 1 (Heat Metal): "Choose a manufactured metal object... creature takes 2d8 fire damage... if holding it, drop it or have disadvantage."  
RETRIEVED RULE 2 (Iron Golem): "Fire Absorption: Whenever the golem is subjected to fire damage, it takes no damage and instead regains hit points."

TASK: Resolve the interaction.

**LLM Output:**

"The spell is successfully cast on the armor. However, because it is an Iron Golem, the 'Fire Absorption' trait triggers. Instead of taking 2d8 damage, the Golem *heals* for that amount. It does not drop its armor."

## **3\. Handling "Rule Disputes"**

Sometimes the AI and Player disagree. We add a **Meta-Channel**.

* **User:** "Wait, I thought I had advantage\!"  
* **System:** Triggers rule\_check intent.  
* **Action:**  
  1. Search DB for "Advantage sources".  
  2. Check SessionContext for active buffs (e.g., "Guiding Bolt: Next attack has advantage").  
  3. If found, reroll math engine.  
  4. If not found, explain: "I see no active effects granting advantage. Are you referring to a specific ability?"

## **4\. Architecture Diagram**

graph TD  
    User\["User: 'I cast Fireball\!'"\] \--\> Parser{Intent Parser}  
      
    Parser \-- "Simple Math" \--\> PythonEngine\[Python Dice Roller\]  
      
    Parser \-- "Complex Magic" \--\> VectorDB\[(SRD Vector DB)\]  
    VectorDB \--\> |Retrieve 'Fireball' Rules| LLM  
      
    PythonEngine \--\> |"Rolled 15 damage"| LLM  
      
    LLM\[Narrative Agent\] \--\> |"The fire explodes..."| Output  
