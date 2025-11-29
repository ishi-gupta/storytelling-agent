# GOAT Story Backend

Flask backend server for the GOAT Storytelling IDE.

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### `GET /api/health`
Health check endpoint to verify server is running.

**Response:**
```json
{
  "status": "ok",
  "message": "GOAT Story Backend is running!",
  "sessions_dir": "/path/to/story_generation_logs"
}
```

### `GET /api/sessions`
Returns all story sessions from `story_generation_logs/` directory.

**Response:**
```json
{
  "sessions": [
    {
      "id": "9",
      "seed": {...},
      "plans": {...},
      "judges": {...},
      "story": "..."
    },
    ...
  ]
}
```

This endpoint provides live data and replaces the need to run `export_sessions.py`.

## Development

- The server runs in debug mode by default (auto-reloads on code changes)
- CORS is enabled to allow React frontend (port 3000) to connect
- All paths are relative, so it works anywhere


