# **Context Assembly Strategy**

To maintain coherence, we build the prompt like a sandwich. The "Meat" (Chat History) is in the middle, but the "Bread" (System Rules & State) holds it together.

## **The Prompt Anatomy**

When you send a request to the AI, the text is structured in this specific order:

### **1\. System Block (The "Constitution")**

*Immutable rules. Never truncated.*

"You are a Dungeon Master running a D\&D 5e game. You must adhere to the dice rolls provided. Do not hallucinate success if the dice say failure. Keep descriptions concise."

### **2\. The "HUD" Block (The "Eyes")**

*The absolute truth of the current moment. Updates every turn.*

**CURRENT STATUS:**

* Location: Room 4 (The Crypt)  
* Player HP: 12/20  
* Enemies: 2x Skeletons (Active)  
* Door State: Locked

### **3\. The Narrative Summary (The "Memory")**

*Compressed bullet points of the session so far.*

**STORY SO FAR:**

* The party entered the crypt at 8:00 PM.  
* They solved the rune puzzle in the hallway.  
* They triggered a trap in Room 2 (took 5 dmg).

### **4\. The Rolling Window (The "Conversation")**

*The last 5-10 raw text exchanges. This allows the AI to understand "it" or "him" references.*

Player: "I attack the left skeleton."

DM: "You swing your sword..."

Player: "Did I hit?"

DM: "Yes, you dealt 6 damage."

Player: \[Current Input\]

## **Logging & Archival Workflow**

To ensure we can reconstruct the game later, we log data in two streams:

### **Stream A: The Transcript (Text)**

Saved as session\_log.txt.