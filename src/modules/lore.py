from typing import List, Dict, Optional
from pydantic import BaseModel, Field, PrivateAttr
from src.core.vector_db import LoreVectorDB

# --- 1. THE KNOWLEDGE ATOMS ---

class LoreFragment(BaseModel):
    """A single piece of information about the world."""
    id: str
    category: str # e.g., "history", "faction", "gods", "geography"
    content: str  # "The Sun King was betrayed by his brother."
    tags: List[str] # ["sun_kingdom", "betrayal", "royal_family"]

    # Secret Management
    is_secret: bool = False
    discovery_dc: int = 15 # Difficulty Check to learn this (History/Arcana)
    known_by_player: bool = False

class AtmosphereProfile(BaseModel):
    """The 'Vibe' of a location."""
    visuals: List[str] # ["crumbling stone", "bioluminescent moss"]
    sounds: List[str] # ["distant dripping", "scuttling claws"]
    smells: List[str] # ["ozone", "rot"]
    lighting: str # "Dim purple glow"

# --- 2. THE CONTEXT CONTAINERS ---

class WorldBible(BaseModel):
    """The Master Encyclopedia (Macro Layer)."""
    world_name: str
    global_lore: List[LoreFragment]
    factions: Dict[str, str] # {"Cult of Worms": "Wants to eat the sun"}

    _vector_db: Optional[LoreVectorDB] = PrivateAttr(default=None)

    # This vector index is conceptual; in prod use ChromaDB/Pinecone
    def query_lore(self, query_tags: List[str]) -> List[LoreFragment]:
        """The 'Librarian': Finds lore relevant to specific tags."""
        # Initialize Vector DB if not already done (Lazy Loading)
        if self._vector_db is None:
            self._vector_db = LoreVectorDB()
            # Index the lore fragments
            self._vector_db.index_lore(self.global_lore)

        # Construct query from tags
        query_text = " ".join(query_tags)

        # Perform semantic search
        relevant_ids = self._vector_db.search(query_text)

        # Retrieve the actual fragment objects
        # Optimization: Map IDs to fragments for quick lookup
        lore_map = {f.id: f for f in self.global_lore}

        relevant_chunks = []
        for rid in relevant_ids:
            if rid in lore_map:
                relevant_chunks.append(lore_map[rid])

        return relevant_chunks

class SessionContext(BaseModel):
    """The 'Cheat Sheet' attached to the Session JSON (Meso Layer).
    This is small enough to fit in the LLM Context Window.
    """
    location_name: str
    atmosphere: AtmosphereProfile

    # We only copy the RELEVANT lore here, not the whole Bible
    local_history: List[LoreFragment]
    local_factions: List[str]

# --- 3. THE INJECTION LOGIC (MESO-GENERATOR) ---

def hydrate_session_with_lore(world_db: WorldBible,
                              location_tags: List[str],
                              biome_type: str) -> SessionContext:
    """
    Runs before the session starts.
    Builds the 'Setting Guide' for this specific adventure.
    """

    # 1. Ask the Librarian for relevant history
    # e.g., location_tags = ["elven_ruins", "forest"]
    relevant_history = world_db.query_lore(location_tags)

    # 2. Generate Atmosphere (can be random or template-based)
    atmosphere = AtmosphereProfile(
        visuals=["vines choking statues", "sunlight filtering through canopy"],
        sounds=["birds chirping nervously", "cracking branches"],
        smells=["pine needles", "old stone"],
        lighting="Dappled sunlight"
    )
    if biome_type == "crypt":
        atmosphere.lighting = "Pitch black"
        atmosphere.smells = ["dust", "stagnant air"]

    # 3. Assemble the Context Package
    context = SessionContext(
        location_name="The Whispering Ruins",
        atmosphere=atmosphere,
        local_history=relevant_history,
        local_factions=["Forest Guardians"]
    )

    return context
