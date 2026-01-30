import random
from typing import Dict, List, Optional
from pydantic import BaseModel

# --- DATA MODELS ---

class RollResult(BaseModel):
    total: int
    natural_roll: int
    modifier: int
    is_crit: bool
    is_fail: bool
    description: str

class CheckRequest(BaseModel):
    character_id: str
    stat_type: str # "strength", "dexterity"
    skill_type: Optional[str] = None # "stealth", "athletics"
    difficulty_class: int

# --- THE CALCULATOR (Deterministic Logic) ---

class DiceEngine:
    @staticmethod
    def roll_d20(modifier: int, advantage: bool = False, disadvantage: bool = False) -> RollResult:
        """Performs the math for a standard check."""
        roll_1 = random.randint(1, 20)
        roll_2 = random.randint(1, 20)

        if advantage and not disadvantage:
            natural = max(roll_1, roll_2)
        elif disadvantage and not advantage:
            natural = min(roll_1, roll_2)
        else:
            natural = roll_1

        total = natural + modifier

        return RollResult(
            total=total,
            natural_roll=natural,
            modifier=modifier,
            is_crit=(natural == 20),
            is_fail=(natural == 1),
            description=f"Rolled {natural} + {modifier} = {total}"
        )

# --- THE ARBITER (Hybrid Logic) ---

class RulesArbiter:
    def __init__(self, character_db: Dict):
        self.char_db = character_db

    def resolve_attack(self, attacker_id: str, target_ac: int, weapon_mod: int) -> str:
        """
        Fast Path: Combat Math.
        We do NOT ask the LLM 'Did he hit?'. We calculate it here.
        """
        roll = DiceEngine.roll_d20(weapon_mod)

        if roll.is_crit:
            return f"CRITICAL HIT! ({roll.description})"
        elif roll.total >= target_ac:
            return f"HIT! ({roll.description} vs AC {target_ac})"
        else:
            return f"MISS. ({roll.description} vs AC {target_ac})"

    def resolve_skill_check(self, request: CheckRequest) -> str:
        """
        Fast Path: Skill Checks.
        """
        # In a real app, look up the mod from the DB
        # char = self.char_db[request.character_id]
        # mod = char.stats[request.stat_type]
        mock_mod = 3

        roll = DiceEngine.roll_d20(mock_mod)

        outcome = "SUCCESS" if roll.total >= request.difficulty_class else "FAILURE"
        return f"{outcome}: {roll.description} vs DC {request.difficulty_class}"
