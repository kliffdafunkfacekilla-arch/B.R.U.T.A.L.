import re
from typing import Dict, List, Optional
from pydantic import BaseModel

# --- DATA MODELS ---

class AudioCue(BaseModel):
    type: str  # "music", "sfx", "ambience"
    resource_id: str # Filename or URI
    volume: float = 1.0
    action: str = "play" # "play", "stop", "fade_in", "fade_out"

class VisualCue(BaseModel):
    type: str # "scene", "portrait", "item"
    prompt: str
    negative_prompt: str
    style_preset: str # "dark_fantasy", "sketch", "pixel_art"

class SceneState(BaseModel):
    location_tags: List[str] # ["crypt", "damp", "stone"]
    tension_level: int # 0 (Calm) to 5 (Boss Fight)
    current_weather: str
    time_of_day: str

# --- THE DIRECTOR ENGINE ---

class MediaDirector:
    def __init__(self):
        # Mappings for Music based on Tension + Biome
        self.music_map = {
            "crypt": {
                0: "ambience_dripping_cave.mp3",
                1: "music_creepy_drone.mp3",
                3: "music_tension_strings.mp3",
                5: "music_boss_choir.mp3"
            },
            "tavern": {
                0: "ambience_crowd_chatter.mp3",
                1: "music_lute_folk.mp3"
            }
        }

        # Keyword triggers for Sound Effects
        self.sfx_triggers = {
            r"\b(hit|slash|cut|damage)\b": "sfx_sword_impact.wav",
            r"\b(miss|dodge|parry)\b": "sfx_sword_whoosh.wav",
            r"\b(fire|burn|flame)\b": "sfx_fireball_explode.wav",
            r"\b(potion|drink|sip)\b": "sfx_bottle_cork.wav",
            r"\b(scream|shriek|roar)\b": "sfx_monster_roar.wav",
            r"\b(gold|coin|loot)\b": "sfx_coin_jingle.wav"
        }

    def analyze_scene_audio(self, narrative_text: str, state: SceneState) -> List[AudioCue]:
        """
        Determines what sounds to play based on the text and game state.
        """
        cues = []

        # 1. MUSIC / AMBIENCE LAYER
        # Check if we need to change the background track based on tension
        # In a real app, we'd cache the 'current_track' to avoid restarting it.
        biome_tracks = self.music_map.get(state.location_tags[0], self.music_map["crypt"])

        # Find the closest tension track (e.g., if tension is 4, play track 3 or 5)
        closest_tension = min(biome_tracks.keys(), key=lambda k: abs(k - state.tension_level))
        selected_track = biome_tracks[closest_tension]

        cues.append(AudioCue(
            type="music",
            resource_id=selected_track,
            action="fade_to",
            volume=0.8
        ))

        # 2. SFX LAYER (Regex Matching)
        # Scan the narrative text for action verbs
        for pattern, sfx_file in self.sfx_triggers.items():
            if re.search(pattern, narrative_text, re.IGNORECASE):
                cues.append(AudioCue(type="sfx", resource_id=sfx_file))

        return cues

    def construct_image_prompt(self, description: str, state: SceneState) -> VisualCue:
        """
        Translates a game description into a Stable Diffusion prompt.
        Ensures consistent style via 'Prompt Engineering' injection.
        """

        # The 'Style Bible' - Hardcoded aesthetic rules
        base_style = "digital painting, dark fantasy art style, greg rutkowski, dramatic lighting, detailed textures, 8k resolution"

        # Context Injection
        lighting = "dimly lit, torchlight" if state.time_of_day == "night" else "dappled sunlight"
        environment = f"{' '.join(state.location_tags)} environment"

        # Final Assembly
        full_prompt = f"{environment}, {description}, {lighting}, {base_style}"
        negative = "blurry, low quality, anime, cartoon, text, watermark, bad anatomy"

        return VisualCue(
            type="scene",
            prompt=full_prompt,
            negative_prompt=negative,
            style_preset="dark_fantasy_v4"
        )
