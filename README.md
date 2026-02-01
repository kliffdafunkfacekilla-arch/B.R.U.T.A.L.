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

*   **Web Interface**: Open `http://localhost:8000` to play the game.
*   **API Status**: Check `http://localhost:8000/health`.
*   **API Docs**: Open `http://localhost:8000/docs` for Swagger UI.

### Configuration

To enable real AI generation:
1.  Obtain a Google Gemini API Key.
2.  Set the environment variable:
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```
    If not set, the system falls back to a simulated mode for testing.

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
*   `src/static`: Frontend HTML/JS/CSS.
*   `data/game_assets`: Generated assets (Images, Audio).
*   `data/sessions`: Saved session states.
