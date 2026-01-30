import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.lore import WorldBible, LoreFragment

def test_semantic_search():
    print("Testing Semantic Search Implementation...")

    # 1. Create dummy lore
    fragments = [
        LoreFragment(id="1", category="beast", content="The Red Dragon burns villages.", tags=["dragon", "fire"]),
        LoreFragment(id="2", category="environment", content="The Ice Queen freezes the lake.", tags=["ice", "cold"]),
        LoreFragment(id="3", category="faction", content="The Thieves Guild operates in shadows.", tags=["thief", "stealth"]),
    ]

    bible = WorldBible(
        world_name="Test World",
        global_lore=fragments,
        factions={}
    )

    # 2. Query for "hot lizard" (should match dragon, semantically)
    # The tags "dragon" and "fire" match "hot lizard" semantically.
    print("\nQuerying: 'hot lizard'...")
    results = bible.query_lore(["hot", "lizard"])
    print(f"Results: {[f.content for f in results]}")

    if not results:
        print("FAIL: No results found for 'hot lizard'")
        sys.exit(1)

    # The first result should be the dragon
    if results[0].id != "1":
        print(f"FAIL: Expected Dragon (id=1), got {results[0].content}")
        sys.exit(1)

    # 3. Query for "frozen water" (should match ice queen)
    print("\nQuerying: 'frozen water'...")
    results = bible.query_lore(["frozen", "water"])
    print(f"Results: {[f.content for f in results]}")

    if not results:
        print("FAIL: No results found for 'frozen water'")
        sys.exit(1)

    if results[0].id != "2":
        print(f"FAIL: Expected Ice Queen (id=2), got {results[0].content}")
        sys.exit(1)

    print("\nSUCCESS: Semantic search works as expected!")

if __name__ == "__main__":
    test_semantic_search()
