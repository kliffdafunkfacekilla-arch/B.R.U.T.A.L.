# **Assembly Guide: The Infinite Dungeon Master Framework**

This guide provides the step-by-step instructions for wiring together the Python backend and React frontend modules.

## **Step 1: The Environment Setup**

**Goal:** Create the folder structure where all your generated scripts will live.

1. **Backend:** Create a Python environment. Install fastapi, pydantic, openai (for Whisper/GPT), and chromadb (for Lore).  
2. **Frontend:** Initialize a React project (Vite or Next.js) and install lucide-react for icons and tailwind-css for styling.  
3. **Folders:**  
   * /server: Python scripts.  
   * /client: React components.  
   * /data: Folder for campaign\_bible.json and asset\_index.json.  
   * /assets: Folders for generated /images and /audio.

## **Step 2: Implementing the "Bible" (Data Layer)**

**Goal:** Establish the source of truth using dungeon\_master\_schemas.py.

1. Initialize your CampaignState object.  
2. When the user first clicks "New Game," run your **Macro-Generator**. Have the AI output a JSON following your PlotPoint schema.  
3. Save this to your /data folder. This is now your permanent "Save File."

## **Step 3: Wiring the Logic Engines (The Brains)**

**Goal:** Connect the Rules, Lore, and Media Directors.

1. **The Librarian:** Import lore\_system\_architecture.py. On startup, load your world history into a Vector Database (ChromaDB).  
2. **The Referee:** Import rules\_engine\_core.py. This script will sit quietly until the AI detects an "Attack" or "Skill Check" intent.  
3. **The Director:** Import media\_director\_engine.py. This script monitors the narrative text coming out of the AI to trigger music and sound effects.

## **Step 4: The "Setup Phase" (Meso-Generation)**

**Goal:** Pre-generate the first adventure.

1. Before the player enters a room, run the **Meso-Generator**.  
2. Have it look at the next PlotPoint in your Macro-Graph.  
3. Generate the SessionModule (the 5-room map).  
4. Trigger the **Asset Cache Manager** (asset\_caching\_system.py) to pre-generate images for these rooms so the player doesn't have to wait.

## **Step 5: The Live Loop (The Heartbeat)**

**Goal:** Connect the main\_orchestrator.py to the STT/TTS services.

1. **Input:** User speaks \-\> Whisper API (STT) \-\> Text.  
2. **Parsing:** Text \-\> intent\_parser.py \-\> JSON Command.  
3. **Resolution:** \* If command is "Attack" \-\> Send to rules\_engine\_core.py.  
   * If command is "Talk" \-\> Send to Narrative LLM \+ Lore Context.  
4. **Output:** \* Resulting Text \-\> ElevenLabs API (TTS) \-\> Audio.  
   * Resulting Visuals \-\> media\_director\_engine.py \-\> CSS/Images.

## **Step 6: Connecting the Frontend (The Dashboard)**

**Goal:** Make the React UI talk to the Python Backend.

1. In your DungeonInterface.jsx, replace the "Mock Logic" with fetch() or axios calls to your Python FastAPI server.  
2. **Websockets (Recommended):** Use a websocket for the logs so the AI can "stream" its narrative word-by-word to the player, making it feel more like a real conversation.  
3. **Audio Manager:** Ensure the React app has a hidden audio player that listens for the AudioCue objects from the backend.

## **Step 7: Local Multiplayer & Voice Diarization**

**Goal:** Calibrate for your friends.

1. **Training:** Use the "Voice Training" mode in the UI to record 5 seconds of audio for each friend.  
2. **Storage:** Save these frequency fingerprints in your PlayerCharacter schema.  
3. **Identification:** At runtime, before processing the intent, the system compares the audio "shape" to the saved fingerprints.  
   * *Backend Logic:* if voice\_match \== "Dave": speaker \= "Grog".  
   * This ensures "Grog" is the one whose HP bar moves on the UI.

## **Execution Flow Diagram**

sequenceDiagram  
    participant Player  
    participant React\_UI  
    participant Python\_Server  
    participant AI\_Services

    Player-\>\>React\_UI: Speaks into Microphone  
    React\_UI-\>\>Python\_Server: Sends Audio Stream  
    Python\_Server-\>\>AI\_Services: Whisper (STT)  
    AI\_Services--\>\>Python\_Server: "I hit the orc"  
    Python\_Server-\>\>Python\_Server: Intent Parser: \[ATTACK\]  
    Python\_Server-\>\>Python\_Server: Rules Engine: \[Roll 1d20+5\] \-\> HIT  
    Python\_Server-\>\>AI\_Services: LLM: Describe hit with \[Gory\] tone  
    AI\_Services--\>\>Python\_Server: "The orc falls..."  
    Python\_Server-\>\>Python\_Server: Media Director: Trigger \[Splat\_SFX\]  
    Python\_Server--\>\>React\_UI: Update HP Bar & Play Audio  
    React\_UI--\>\>Player: DM Voice: "The orc falls..." \+ Sound Effect  
