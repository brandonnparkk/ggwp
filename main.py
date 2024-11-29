import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class GameCreateRequest(BaseModel):
    game_name: str
    players: list[dict]  # List of player objects with 'name'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://splendorous-muffin-58a087.netlify.app"],  # Frontend URL
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users")
async def get_users():
    try:
        # Query the `users` table
        response = supabase.table("users").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/game/{game_id}")
async def get_game_details(game_id: str):
    try:
        # Query players and decks
        players_query = supabase.rpc("get_players_and_decks", {"game_id": game_id}).execute()
        if not players_query.data:
            raise HTTPException(status_code=404, detail="Game or players not found")

        players_and_decks = players_query.data

        # Query game results
        results_query = supabase.rpc("get_game_results", {"game_id": game_id}).execute()
        game_results = results_query.data if results_query.data else []

        # Combine results into a single response
        response = {
            "game_id": game_id,
            "players": players_and_decks,
            "results": game_results
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/game")
async def create_game(game: GameCreateRequest):
    try:
        data = {
            "game_name": game.game_name,
            "players": game.players,
        }

        response = supabase.table("games").insert(data).execute()

        return {"message": "Game created successfully", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# class Task(BaseModel):
#     id: Optional[UUID] = None
#     title: str
#     description: Optional[str] = None
#     completed: Optional[bool] = False

# tasks = []

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# @app.get("/tasks/{task_id}", response_model=Task)
# def read_task(task_id: UUID):
#     for task in tasks:
#         if task.id == task_id:
#             return task

#     raise HTTPException(status_code=404, detail="task not found!")

# @app.get("/tasks/", response_model=List[Task])
# def read_tasks():
#     return tasks

# @app.post("/tasks/", response_model=Task)
# def create_tasks(task: Task):
#     task.id = uuid4()
#     tasks.append(task)
#     return task

# @app.put("/tasks/${task_id}", response_model=Task)
# def update_task(task_id: UUID, task_update: Task):
#     for index, task in enumerate(tasks):
#         if task.id == task_id:
#             updated_task = task.copy(update=task_update.dict(exclude_unset=True))
#             task[index] = updated_task
#             return updated_task

#     raise HTTPException(status_code=404, detail=f"Could not find task {task_id} to update")

# @app.delete("/tasks/${task_id}", response_model=Task)
# def delete_task(task_id: UUID):
#     for index, task in enumerate(tasks):
#         if task.id == task_id:
#             return tasks.pop(index)

#     raise HTTPException(status_code=404, detail=f"Task was not found!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)