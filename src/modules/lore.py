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
    factions: Dict[str, str] # {"Cult of Worms": "Wants to eat the sun"}

    # Store global_lore temporarily for ingestion, but clear it to save memory.
    global_lore: List[LoreFragment] = Field(default_factory=list)

    # Path for vector DB persistence
    db_path: Optional[str] = "./data/vector_store"

    _vector_db: Optional[LoreVectorDB] = PrivateAttr(default=None)

    def query_lore(self, query_tags: List[str]) -> List[LoreFragment]:
        """The 'Librarian': Finds lore relevant to specific tags."""
        # Initialize Vector DB if not already done (Lazy Loading)
        if self._vector_db is None:
            self._vector_db = LoreVectorDB(persistence_path=self.db_path)
            # Index the lore fragments if we have pending ones
            if self.global_lore:
                self._vector_db.index_lore(self.global_lore)
                # Clear memory after indexing
                self.global_lore = []

        # Construct query from tags
        query_text = " ".join(query_tags)

        # Perform semantic search
        # Now returns list of dicts (parsed JSON)
        results = self._vector_db.search(query_text)

        relevant_chunks = []
        for res_dict in results:
            try:
                # Convert back to LoreFragment
                fragment = LoreFragment.model_validate(res_dict)
                relevant_chunks.append(fragment)
            except Exception as e:
                print(f"Error parsing lore fragment: {e}")

        return relevant_chunks

    def ingest_lore(self, fragments: List[LoreFragment]):
        """Manually ingest new lore into the database."""
        if self._vector_db is None:
             self._vector_db = LoreVectorDB(persistence_path=self.db_path)
        self._vector_db.index_lore(fragments)

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
