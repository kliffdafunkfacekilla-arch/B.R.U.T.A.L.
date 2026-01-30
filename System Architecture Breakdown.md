# **The AI Dungeon Master: A Functional Breakdown**

This document explains the "Macro-Meso-Micro" architecture in simple terms, using the analogy of a Film Production Studio.

## **1\. The Core Data (The "Series Bible")**

**What it is:** The memory of the system.

**Why you need it:** AI models have short memories. If you play for 2 hours, the AI will forget who the villain is unless you write it down in a structured way.

* **Campaign Schema (campaign.json):** This is the "World Encyclopedia." It stores things that never change or change slowly (e.g., "The King is corrupt," "Elves hate Dwarves").  
* **Session Schema (session.json):** This is the "Clipboards" for tonight's game. It stores temporary things (e.g., "The goblin in Room 4 has 5 HP left," "The door to Room 2 is locked").  
* **The Knowledge Graph:** Think of this like a detective's corkboard with red string. It connects dots: NPC A \--(is secretly)--\> The Villain.

## **2\. The Macro-Generator (The "Showrunner")**

**What it is:** The "Setup Phase" you described. This runs *once* at the very beginning.

**Why you need it:** To ensure the story has a beginning, middle, and end, rather than just random events.

* **The World Gen Agent:** You say "Cyberpunk Heist," and it writes the season arc: "Act 1: Get the Crew. Act 2: Steal the Data. Act 3: Escape."  
* **The Plot Point Segmenter:** It takes "Act 1" and breaks it into specific milestones. It draws a roadmap so the AI knows where to steer the car even if the players drive off-road.

## **3\. The Meso-Generator (The "Set Designer")**

**What it is:** The "Granular" layer. This runs *between* sessions (or quietly in the background).

**Why you need it:** This is the "Module Builder" logic. It prepares the math and geography so the runtime AI doesn't have to panic-invent everything.

* **Dungeon Designer:** The Macro layer says "The players go to a Crypt." This agent actually draws the 5 rooms of the Crypt, decides where the traps are, and hides the key under the mat in Room 3\.  
* **The Rules Lawyer (Prep):** It looks at the monsters in the Crypt and pre-calculates their stats (HP, Armor, Damage) based on the player's level, saving this to a file.

## **4\. The Micro-Engine (The "Actor & Referee")**

**What it is:** The actual loop that happens when you are talking to the computer.

**Why you need it:** To process your voice and enforce the rules in real-time.

* **Input Router (The Ears):** It listens to your voice (STT). It decides: "Are they asking a question?" or "Are they swinging a sword?"  
* **State Checker (The Referee):** If you say "I open the door," this piece checks the session.json. Is the door locked? Do you have the key? It creates boundaries.  
* **Narrative Generator (The Mouth):** It describes what happens using the TTS (Text-to-Speech) voice. "The door creaks open, revealing a skeleton."

## **5\. The Asset Pipeline (The "Illustrator")**

**What it is:** The visual generator.

**Why you need it:** Immersion.

* **Map Renderer:** It takes the data from the Meso-Generator (e.g., "Room is 20x20 ft") and draws a grid image for you to look at.  
* **Portrait Gen:** When a new NPC walks in, it generates a face so you aren't just looking at text.

## **6\. Testing (The "Rehearsal")**

**What it is:** Automated bots that try to break the game.

**Why you need it:** AI often hallucinates logic errors (e.g., allowing you to walk through walls).

* **The Murder Hobo Bot:** A program that just attacks everything. We run this to make sure the story adapts properly if the players decide to kill the quest giver.  
* **The Speedrunner Bot:** Tries to skip the plot. We use this to verify that the "Locked Doors" and "Barriers" generated in Phase 3 actually work.