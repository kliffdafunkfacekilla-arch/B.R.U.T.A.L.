import time
import asyncio
from src.modules.llm_gateway import LLMGateway
from src.modules.intent_parser import IntentParser
from src.core.session_manager import SessionManager
# from src.models.dungeon import RoomNode
from src.core.table_engine import TableLogicEngine
# from src.modules.lore import hydrate_session_with_lore

async def run_game_loop():
    print("--- INITIALIZING AI DUNGEON MASTER ---")

    # 1. SETUP PHASE (Macro & Meso Layers)
    llm = LLMGateway(api_key="sk-...")
    parser = IntentParser(llm)
    logic_engine = TableLogicEngine(player_level=1, biome="dungeon")

    # Load session
    session_manager = SessionManager()
    session = session_manager.load_session("demo_session")

    # Get initial room (assuming room_01 exists in default session)
    if "room_01" in session.rooms:
        current_room = session.rooms["room_01"]
    else:
        # Fallback if room_01 missing (shouldn't happen with default creator)
        print("Error: room_01 not found in session. Exiting.")
        return
    # Simulate loading the "Session" we generated earlier
    current_room = {
        "id": "room_01",
        "title": "Damp Crypt",
        "exits": ["north"],
        "entities": [{
            "name": "Goblin Scavenger",
            "hp_current": 7,
            "hp_max": 7
        }],
        "loot": [],
        "description_initial": "A cold, damp crypt."
    }

    # 2. START GAME LOOP (Micro Layer)
    game_running = True
    while game_running:

        # A. INPUT (STT)
        # In a real app, this waits for microphone input
        try:
            user_audio = input("\n🎤 You (Type to simulate voice): ")
        except EOFError:
            break

        if user_audio == "quit":
            break

        # Extract entity names for parser
        valid_targets = [e.name for e in current_room.entities]

        # B. INTENT PARSING (Logic Router)
        # The Parser looks at valid targets in the room to help the AI decide
        valid_targets = [e['name'] for e in current_room['entities']]
        user_intent = parser.parse_input(user_audio, valid_targets=valid_targets)
        print(f"⚙️ [SYSTEM PARSED]: {user_intent}")

        # C. LOGIC EXECUTION (State Update)
        # We pass the intent to the TableLogicEngine (from previous steps)
        # result = logic_engine.process_action(user_intent, current_room)

        # Simulating Logic Result:
        if user_intent.get('action') == 'attack':
            logic_result = "Success. Goblin takes 5 damage. Goblin dies."
            current_room.entities = [] # Update State
            # Optionally save state: session_manager.save_session(session)
        else:
            logic_result = "You look around. Nothing happens."
        logic_result = logic_engine.process_player_action(user_intent.get('action'), current_room)

        # D. NARRATIVE GENERATION (The Storyteller)
        # Combine the Logic Result with the Lore/Atmosphere
        narrative_prompt = f"""
        Action Result: {logic_result}
        Current Room: {current_room.title}
        Lore Context: Goblins here fear fire.

        Write a 2-sentence description of this outcome.
        """

        story_output = await llm.generate_narrative("You are a DM.", narrative_prompt)

        # E. OUTPUT (TTS)
        llm.text_to_speech(story_output)

if __name__ == "__main__":
    asyncio.run(run_game_loop())
