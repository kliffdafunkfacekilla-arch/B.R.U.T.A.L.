# **System Logic Flow**

## **1\. The Creation Pipeline (Macro to Meso)**

This flow runs *before* the player starts the game. It turns a simple prompt into a playable JSON structure.

graph TD  
    UserInput\["User Prompt: 'A Sci-Fi Prison Break'"\] \--\> MacroGen\[Macro Generator Agent\]  
      
    subgraph Macro Layer  
        MacroGen \--\> StoryGraph\[Generate Plot Graph (DAG)\]  
        StoryGraph \--\> SelectNode{Select Current Plot Node}  
        SelectNode \--\> |"Start at the Prison Cell"| CurrentContext\[Context Definition\]  
    end  
      
    subgraph Meso Layer  
        CurrentContext \--\> DungeonGen\[Dungeon Layout Agent\]  
        DungeonGen \--\> Skeleton\[Create Room Skeleton (Nodes & Edges)\]  
          
        Skeleton \--\> Populator\[Content Populator Agent\]  
          
        subgraph Table Logic  
            Populator \--\> ThemeTable\[Select Theme/Biome\]  
            Populator \--\> MonsterTable\[Roll Encounter Table\]  
            Populator \--\> LootTable\[Roll Loot Table\]  
        end  
          
        ThemeTable & MonsterTable & LootTable \--\> JSON\[Construct 'session\_module.json'\]  
    end  
      
    JSON \--\> Ready\[Ready for Session\]

## **2\. The Runtime Loop (Micro)**

This flow runs *during* the game. It handles the "I open the door" logic.

sequenceDiagram  
    participant User  
    participant STT as Whisper STT  
    participant Router as Logic Router  
    participant Engine as Table Engine  
    participant JSON as Session JSON  
    participant TTS as ElevenLabs TTS

    User-\>\>STT: "I kick open the North door\!"  
    STT-\>\>Router: Text: "Kick open North door"  
      
    Router-\>\>Router: Parse Intent: ACTION (Move/Force)  
      
    rect rgb(30, 30, 30\)  
        Note right of Router: Validation Step  
        Router-\>\>JSON: Check Room('current').exits\['north'\]  
        JSON--\>\>Router: Returns Room('room\_02')  
        Router-\>\>JSON: Check Room('room\_02').is\_locked?  
    end  
      
    alt Door is Locked  
        Router-\>\>Engine: Calculate Strength Check (DC 15\)  
        Engine--\>\>Router: Result: Failure  
        Router-\>\>TTS: "You kick the door, but it holds firm. Your foot hurts."  
    else Door Opens  
        Router-\>\>JSON: Update current\_room \= 'room\_02'  
        Router-\>\>JSON: Set room\_02.is\_visited \= True  
        JSON--\>\>Router: Return Room Description & Entities  
        Router-\>\>TTS: "The door crashes open\! You see a Goblin Guard..."  
    end  
      
    TTS-\>\>User: Audio Playback

## **3\. The Table Flow Logic (Decision Tree)**

How the AI decides what is in a room when generating it.

graph LR  
    Start\[Generate Room 3\] \--\> TypeCheck{Is it a Boss Room?}  
      
    TypeCheck \-- Yes \--\> BossLogic\[Load 'Boss' Table\]  
    BossLogic \--\> GenBoss\[Spawn Unique NPC\]  
    GenBoss \--\> HighLoot\[Spawn Rare Loot\]  
      
    TypeCheck \-- No \--\> DiffCheck{Difficulty Check}  
      
    DiffCheck \--\> |Roll 1d6| RandomCheck  
      
    RandomCheck \-- 1-2 \--\> Empty\[Empty Room\]  
    RandomCheck \-- 3-5 \--\> Minion\[Standard Encounter\]  
    RandomCheck \-- 6 \--\> Trap\[Trap Room\]  
      
    Minion \--\> CRCalc\[Calculate CR Budget\]  
    CRCalc \--\> SelectMon\[Select Monsters \< Budget\]  
      
    Empty & Trap & SelectMon \--\> Finalize\[Commit to JSON\]  
