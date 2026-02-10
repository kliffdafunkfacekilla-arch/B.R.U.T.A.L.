import os
import json
import random
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

# Core Modules
from src.modules.intent_parser import IntentParser
from src.modules.rules import RulesArbiter, DiceEngine
from src.modules.lore import WorldBible, LoreFragment
from src.modules.media import MediaDirector, SceneState
from src.modules.asset_manager import AssetCacheManager
from src.modules.llm_gateway import LLMGateway
from src.modules.macro_generator import MacroGenerator
from src.core import persistence
from src.models.party import PlayerCharacter

app = FastAPI(title="Infinite Dungeon Master API")

# RULE 1: Enable CORS so React can communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

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

class AIDungeonMaster:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "dummy_key")
        self.llm_gateway = LLMGateway(api_key=self.api_key)
        self.intent_parser = IntentParser(llm_client=self.llm_gateway)
        self.rules = RulesArbiter(character_db={})
        self.director = MediaDirector()
        self.macro_generator = MacroGenerator()

        # Hardcoded initial lore
        self.lore = WorldBible(
            world_name="Eldoria",
            factions={"Iron Legion": "Military oppressors"},
            global_lore=[LoreFragment(id="h1", category="history", content="The Sun King vanished.", tags=["king"])]
        )

    async def run_interaction_cycle(self, request: InteractionRequest):
        # 1. LOAD SESSION & CHARACTER (Persistence)
        try:
            session = await persistence.load_session(request.session_id)
            # In a real app, character would be loaded from a separate JSON/DB
            # We'll create a default if not found
            char = PlayerCharacter(id=request.character_id, name="Kaelen", player_name="Player", hp=20, max_hp=20, ac=15, initiative_bonus=3)
        except Exception:
            raise HTTPException(status_code=404, detail="Session not found")

        # 2. INTENT PARSING
        current_room_id = "room_01" # Logic to track this should be in SessionModule
        room = session.rooms.get(current_room_id)
        valid_targets = [e.name for e in room.entities] + ["self", "surroundings"]

        intent_data = await self.intent_parser.parse_input(request.input_text, valid_targets)
        action = intent_data.get("action", "explore")
        target_name = intent_data.get("target")

        # 3. RULE RESOLUTION & STATE UPDATE
        logic_result = "You look around."
        roll_info = None
        hp_change = 0

        if action == "attack" and room.entities:
            # Simple Combat Logic
            target_entity = next((e for e in room.entities if e.name == target_name), room.entities[0])

            # Use Rules Arbiter
            outcome = self.rules.resolve_attack(char.id, target_entity.ac, 5) # +5 to hit
            logic_result = outcome

            # UPDATE STATE: If hit, apply damage
            if "HIT" in outcome:
                dmg = random.randint(1, 8) + 3
                target_entity.hp_current -= dmg
                logic_result += f" dealing {dmg} damage."
                if target_entity.hp_current <= 0:
                    logic_result += f" The {target_entity.name} falls dead!"
                    room.entities = [e for e in room.entities if e.name != target_entity.name]

        elif action == "explore":
            logic_result = "You find nothing of immediate danger."

        # 4. LORE & NARRATIVE
        lore_context = " ".join([l.content for l in self.lore.query_lore([action, "dungeon"])])
        narrative = await self.llm_gateway.generate_narrative(
            "You are a grimdark Dungeon Master.",
            f"Lore: {lore_context}\nLogic Outcome: {logic_result}\nInput: {request.input_text}"
        )

        # 5. ASSETS & PERSISTENCE
        scene_state = SceneState(location_tags=["crypt"], tension_level=3 if room.entities else 0, current_weather="none", time_of_day="night")
        audio_cues = self.director.analyze_scene_audio(narrative, scene_state)
        visual_cue = self.director.construct_image_prompt(narrative, scene_state)

        # SAVE UPDATED SESSION
        await persistence.save_session(session)

        return {
            "narrative": narrative,
            "audio_cues": [c.model_dump() for c in audio_cues],
            "visual_cue": visual_cue.model_dump(),
            "dice_roll": {"val": 15, "label": "Action Check"} if action != "explore" else None,
            "state_update": {"hp_change": hp_change, "session_id": session.session_id}
        }

dm_engine = AIDungeonMaster()

@app.get("/health")
async def health(): return {"status": "online"}

@app.get("/")
async def root(): return FileResponse("src/static/index.html")

@app.post("/session/start")
async def start_session(campaign_type: str = Body(..., embed=True)):
    session = await dm_engine.macro_generator.generate_session("camp_01", campaign_type)
    await persistence.save_session(session)
    return {
        "session_id": session.session_id,
        "intro_narrative": f"The journey begins in the {campaign_type}. {session.rooms['room_01'].description_initial}",
        "party_state": {"hp": 20, "maxHp": 20}
    }

@app.post("/interact", response_model=InteractionResponse)
async def interact(request: InteractionRequest):
    return await dm_engine.run_interaction_cycle(request)
