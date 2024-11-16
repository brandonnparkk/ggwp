from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4

app = FastAPI()

class Task(BaseModel):
    id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    completed: Optional[bool] = False

tasks = []

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: UUID):
    for task in tasks:
        if task.id == task_id:
            return task

    raise HTTPException(status_code=404, detail="task not found!")

@app.get("/tasks/", response_model=List[Task])
def read_tasks():
    return tasks

@app.post("/tasks/", response_model=Task)
def create_tasks(task: Task):
    task.id = uuid4()
    tasks.append(task)
    return task

@app.put("/tasks/${task_id}", response_model=Task)
def update_task(task_id: UUID, task_update: Task):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = task.copy(update=task_update.dict(exclude_unset=True))
            task[index] = updated_task
            return updated_task

    raise HTTPException(status_code=404, detail=f"Could not find task {task_id} to update")

@app.delete("/tasks/${task_id}", response_model=Task)
def delete_task(task_id: UUID):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            return tasks.pop(index)

    raise HTTPException(status_code=404, detail=f"Task was not found!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)