# **Multimedia Asset Pipeline Strategy**

To create an immersive experience, we treat assets as **Dynamic Layers**, not static files.

## **1\. Visuals: The "Style Bible" Protocol**

The biggest risk with AI Image Gen is inconsistency (one room looks like a photo, the next like a cartoon). We solve this with **Style Enforcers**.

### **A. The Tech Stack**

* **Engine:** Stable Diffusion XL (SDXL) or Flux.1 (via API like Replicate or run locally).  
* **Consistency Tool:** **LoRA (Low-Rank Adaptation)**.  
  * Train/Download a specific LoRA for "D\&D Oil Painting" style.  
  * Force every prompt to use this LoRA \<lora:dnd\_oil\_v2:0.8\>.

### **B. Prompt Templating**

Never send just the user's description. Wrap it in a sandwich:

1. **Prefix (The Vibe):** "A gloomy dungeon chamber, wide angle shot..."  
2. **Subject (The Content):** "...a goblin warrior holding a rusted dagger..."  
3. **Suffix (The Style):** "...unreal engine 5 render, volumetric fog, dark fantasy, masterpiece."

### **C. Depth Control (ControlNet)**

*Advanced Feature:* Use the *Map Layout* (the grid from the Meso-Generator) as a **ControlNet Input**.

* **Input:** A black-and-white grid of the room shape.  
* **Output:** An AI painting that perfectly matches the geometry of the map (walls are where they should be).

## **2\. Audio: The "Vertical Mixing" System**

We don't just play one song. We mix 3 layers of audio in the browser.

### **Layer 1: The Bed (Ambience)**

* **What:** Seamless loops (Wind, Dripping Water, Tavern Noise).  
* **Behavior:** Loops forever. Changes only when moving biomes (Crypt \-\> Forest).  
* **Source:** Local MP3 library (low bandwidth).

### **Layer 2: The Mood (Music)**

* **What:** Instrumental tracks.  
* **Behavior:** Fades in/out based on tension\_level.  
  * *Tension 0:* Silence or light drone.  
  * *Tension 1-2:* Mysterious melody.  
  * *Tension 5:* Heavy drums.  
* **Technique:** Use **Crossfading** (2 seconds) so the transition isn't jarring.

### **Layer 3: The Stingers (SFX)**

* **What:** Short events (Sword Clang, Roar, Coin Jingle).  
* **Behavior:** One-shot triggers based on Regex keywords in the text.  
* **Source:** Pre-cached library. AI generation for SFX is too slow for real-time combat; stick to a library of 100 common sounds.

## **3\. Voice: The "Casting Director"**

We use TTS (Text-to-Speech) with dynamic voice assignment.

### **Dynamic Casting Map**

When a new NPC is generated in the SessionSchema:

1. **Analyze Tags:** \["orc", "male", "angry"\]  
2. **Select Voice ID:** Map these tags to an ElevenLabs/OpenAI Voice ID.  
   * *Orc/Ogre:* Pitch \-20%, Speed 80% (Deep & Slow).  
   * *Elf/Fairy:* Pitch \+10%, Stability 30% (Light & Breath-y).  
3. **Persistence:** Save this voice\_id to the NPC's JSON entry so they sound the same next time you meet them.

### **Narrative vs. Dialogue**

* **Narrator Voice:** Neutral, authoritative, clear (The DM).  
* **NPC Voice:** Heavily stylized, acted (The Characters).  
* *Implementation:* Split the text string.  
  * Text: *"You see the goblin. He shouts, 'Get them\!'"*  
  * Audio 1 (DM): "You see the goblin. He shouts,"  
  * Audio 2 (Goblin Voice): "Get them\!"