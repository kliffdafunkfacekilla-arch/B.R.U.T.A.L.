# Infinite Dungeon Master

An AI-driven RPG campaign generation and runtime system. This project uses a Macro-Meso-Micro architecture to generate consistent, immersive D&D-like adventures.

## Architecture

*   **Macro-Generator**: Creates the high-level campaign structure (World, Plot).
*   **Meso-Generator**: Generates specific sessions and dungeons (Rooms, Monsters, Loot).
*   **Micro-Engine**: Handles real-time player interaction (Intent Parsing, Rule Resolution, Narrative Generation).

See `System Architecture Breakdown.md` for more details.

## Installation

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running the Server

Start the FastAPI server:

```bash
uvicorn src.api.server:app --reload
```

The API will be available at `http://localhost:8000`.
API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

### Key Endpoints

*   `POST /session/start`: Initialize a new session.
    *   Body: `{"campaign_type": "dark fantasy"}`
*   `POST /interact`: Interact with the DM.
    *   Body:
        ```json
        {
          "user_id": "user1",
          "character_id": "char1",
          "input_text": "I open the door",
          "session_id": "sess_..."
        }
        ```

## Testing

Run the test suite using `pytest`:

```bash
python -m pytest tests
```

## Project Structure

*   `src/api`: FastAPI server and endpoints.
*   `src/core`: Core engines (Game Loop, Table Logic, Persistence).
*   `src/models`: Pydantic data models (Dungeon, Party).
*   `src/modules`: AI and Logic modules (Intent Parser, LLM Gateway, etc.).
*   `data/game_assets`: Generated assets (Images, Audio).
*   `data/sessions`: Saved session states.

## Configuration

*   Set `GEMINI_API_KEY` environment variable to use the real LLM (future feature). Currently uses a simulated LLM.
