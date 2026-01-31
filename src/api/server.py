import os
import json
import random
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Imports from our modules
from src.modules.intent_parser import IntentParser
from src.modules.rules import RulesArbiter, DiceEngine
from src.modules.lore import WorldBible, hydrate_session_with_lore, LoreFragment
from src.modules.media import MediaDirector, SceneState
from src.modules.asset_manager import AssetCacheManager
from src.modules.llm_gateway import LLMGateway
from src.modules.macro_generator import MacroGenerator
from src.core import persistence

app = FastAPI(title="Infinite Dungeon Master API")

# Mount static files (Frontend)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# --- DATA MODELS FOR API ---

class InteractionRequest(BaseModel):
    user_id: str
    character_id: str
    input_text: str
    session_id: str

class InteractionResponse(BaseModel):
    narrative: str
    audio_cues: List[dict]
    visual_cue: dict
    state_update: dict
    dice_roll: Optional[dict] = None

# --- CORE SYSTEM INITIALIZATION ---

class AIDungeonMaster:
    """The Orchestrator that ties all sub-engines together."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "dummy_key")

        # Initialize sub-engines
        self.llm_gateway = LLMGateway(api_key=self.api_key)
        self.intent_parser = IntentParser(llm_client=self.llm_gateway)

        # In a real app, we'd load these from a DB
        self.rules = RulesArbiter(character_db={})

        # Initialize World Bible with some dummy data
        self.lore = WorldBible(
            world_name="Eldoria",
            global_lore=[
                LoreFragment(id="h1", category="history", content="The Elves vanished in the Red Year.", tags=["elf", "history"]),
            ],
            factions={"Iron Legion": "Military oppressors"}
        )

        self.director = MediaDirector()
        self.cache = AssetCacheManager()
        self.macro_generator = MacroGenerator()

    async def run_interaction_cycle(self, request: InteractionRequest):
        """
        THE CORE LOOP:
        1. Intent Parsing
        2. Rule Resolution (Dice/Stats)
        3. Lore Retrieval
        4. Narrative Generation
        5. Media Cue Extraction
        """

        # LOAD SESSION
        try:
            session = await persistence.load_session(request.session_id)
        except Exception:
            # Fallback for testing if session doesn't exist on disk
            # In production, this should raise 404
            print(f"Session {request.session_id} not found, proceeding with mock.")
            session = None

        # STEP 1: PARSE INTENT (NLU)
        # We need a list of valid targets from the current state (mocked here)
        valid_targets = ["goblin_01", "door"]
        if session:
            # Get targets from current room (assuming room_01 for now or track it)
            # For simplicity, let's say we are in room_01 if not specified
            current_room_id = "room_01" # TODO: Track current room in session
            if current_room_id in session.rooms:
                room = session.rooms[current_room_id]
                valid_targets = [e.name for e in room.entities] + list(room.exits.keys()) + ["self"]

        intent_data = await self.intent_parser.parse_input(request.input_text, valid_targets=valid_targets)
        intent = intent_data.get("action", "explore")

        # STEP 2: RULE RESOLUTION
        roll_data = None
        logic_result = "Action acknowledged."

        if intent == "attack":
            # Using the rules engine
            # In a real app, we'd fetch stats from DB
            result_str = self.rules.resolve_attack(
                attacker_id=request.character_id,
                target_ac=12,
                weapon_mod=5
            )
            logic_result = result_str
            # Extract roll for UI (simplification)
            roll_data = {"type": "d20", "val": 0, "label": "See Description"} # The arbiter returns a string, ideally it should return the object

        # STEP 3: LORE RETRIEVAL (RAG)
        # Mocking location tags
        relevant_lore = self.lore.query_lore(["elf"])
        lore_context = " ".join([l.content for l in relevant_lore])

        # STEP 4: NARRATIVE GENERATION (The Storyteller)
        prompt = f"""
        Context: {lore_context}
        Action Result: {logic_result}
        Input: {request.input_text}
        Write a 2-sentence immersive DM response.
        """

        narrative = await self.llm_gateway.generate_narrative("You are a DM", prompt)

        # STEP 5: MEDIA DIRECTOR (Cues)
        # Mocking SceneState
        scene_state = SceneState(
            location_tags=["crypt"],
            tension_level=2,
            current_weather="foggy",
            time_of_day="night"
        )

        audio_cues = self.director.analyze_scene_audio(narrative, scene_state)
        visual_cue = self.director.construct_image_prompt(narrative, scene_state)

        # Convert Pydantic models to dicts for API response
        audio_cues_dicts = [cue.model_dump() for cue in audio_cues]
        visual_cue_dict = visual_cue.model_dump()

        # SAVE SESSION (if loaded)
        if session:
            # Here we would update the session state based on logic_result
            # For now, just saving to prove persistence works
            await persistence.save_session(session)

        return {
            "narrative": narrative,
            "audio_cues": audio_cues_dicts,
            "visual_cue": visual_cue_dict,
            "dice_roll": roll_data,
            "state_update": {"hp_change": -2 if "damage" in narrative.lower() else 0}
        }

# --- API ENDPOINTS ---

dm_engine = AIDungeonMaster()

@app.get("/health")
async def health():
    return {"status": "AI Dungeon Master is online"}

@app.get("/")
async def root():
    return FileResponse("src/static/index.html")

@app.post("/session/start")
async def start_session(campaign_type: str = Body(..., embed=True)):
    """Initializes a new campaign and generates the Macro-Story."""
    # Run Macro-Generator logic
    session = await dm_engine.macro_generator.generate_session(campaign_id="camp_001", prompt=campaign_type)

    # Save the session
    await persistence.save_session(session)

    # Generate intro narrative using the first room
    first_room = session.rooms["room_01"]

    return {
        "session_id": session.session_id,
        "intro_narrative": f"You find yourself in a {campaign_type} world. {first_room.description_initial}",
        "party_state": {"members": []}
    }

@app.post("/interact", response_model=InteractionResponse)
async def interact(request: InteractionRequest):
    """The main gameplay endpoint called by the React frontend."""
    try:
        result = await dm_engine.run_interaction_cycle(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/character/{char_id}")
async def get_character_sheet(char_id: str):
    """Returns the full JSON character sheet."""
    # Fetch from DB
    return {"id": char_id, "name": "Grog", "stats": {"STR": 18}}

# --- MULTIPLAYER / VOICE ENDPOINTS ---

@app.post("/voice/calibrate")
async def calibrate_voice(player_id: str, audio_blob: bytes = Body(...)):
    """Saves a voice frequency fingerprint for local diarization."""
    # Logic to process audio into a vector and save to Player profile
    return {"status": "success", "player_id": player_id}

# --- START SERVER ---
if __name__ == "__main__":
    import uvicorn
    # In a local environment, run: uvicorn src.api.server:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
