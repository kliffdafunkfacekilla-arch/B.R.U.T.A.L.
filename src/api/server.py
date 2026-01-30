import os
import json
import random
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

# Imports from our modules
from src.modules.intent_parser import IntentParser
from src.modules.rules import RulesArbiter, DiceEngine
from src.modules.lore import WorldBible, hydrate_session_with_lore, LoreFragment
from src.modules.media import MediaDirector, SceneState
from src.modules.asset_manager import AssetCacheManager
from src.modules.llm_gateway import LLMGateway

app = FastAPI(title="Infinite Dungeon Master API")

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

    async def run_interaction_cycle(self, request: InteractionRequest):
        """
        THE CORE LOOP:
        1. Intent Parsing
        2. Rule Resolution (Dice/Stats)
        3. Lore Retrieval
        4. Narrative Generation
        5. Media Cue Extraction
        """

        # STEP 1: PARSE INTENT (NLU)
        # We need a list of valid targets from the current state (mocked here)
        valid_targets = ["goblin_01", "door"]
        intent_data = self.intent_parser.parse_input(request.input_text, valid_targets=valid_targets)
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

        narrative = self.llm_gateway.generate_narrative("You are a DM", prompt)

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
        audio_cues_dicts = [cue.dict() for cue in audio_cues]
        visual_cue_dict = visual_cue.dict()

        return {
            "narrative": narrative,
            "audio_cues": audio_cues_dicts,
            "visual_cue": visual_cue_dict,
            "dice_roll": roll_data,
            "state_update": {"hp_change": -2 if "damage" in narrative.lower() else 0}
        }

# --- API ENDPOINTS ---

dm_engine = AIDungeonMaster()

@app.get("/")
async def root():
    return {"status": "AI Dungeon Master is online"}

@app.post("/session/start")
async def start_session(campaign_type: str = Body(..., embed=True)):
    """Initializes a new campaign and generates the Macro-Story."""
    # Run Macro-Generator logic
    return {
        "session_id": "sess_999",
        "intro_narrative": f"You find yourself in a {campaign_type} world. The journey begins...",
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
