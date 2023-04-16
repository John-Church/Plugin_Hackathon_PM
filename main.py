# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Any
import modal
from fastapi.middleware.cors import CORSMiddleware


from linear_types import Issue
from linear_client import LinearClient

app = FastAPI()
stub = modal.Stub("form_generator")

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
origins = [
    "https://chat.openai.com",
    "http://localhost",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

linear_client = LinearClient(endpoint="https://api.linear.app/graphql")


class Task(BaseModel):
    name: str
    description: Optional[str] = None


from linear_client import IssueInput


@app.get("/issues/", response_model=List[Issue])
async def list_issues():
    response = linear_client.list_issues()
    return response


@app.post("/issues/", response_model=Issue)
async def create_issue(issue: IssueInput):
    response = linear_client.create_issue(issue)
    return response


@app.patch("/issues/{issue_id}", response_model=Issue)
async def patch_issue(issue_id: str, issue: IssueInput):
    response = linear_client.update_issue(issue_id, issue)
    return response

@app.get("/issues/{issueId}", response_model=Issue)
async def get_issue(issueId: str):
    """Look up details for a specific issue."""
    response = linear_client.get_issue(issueId)
    return response

@app.post("/webhooks/linear")
async def webhooks_linear(request: Request):
    # TODO: validate sig
    j = await request.json()
    print("webhook payload:")
    print(json.dumps(j))
    return "ok"


# Create a custom image with the required dependencies installed
# image = modal.Image.debian_slim().pip_install()
image = modal.Image.debian_slim().pip_install("requests")
template_mount = modal.Mount.from_local_file(
    ".well-known/ai-plugin.json", remote_path="/root/.well-known/ai-plugin.json"
)
asset_mount = modal.Mount.from_local_file(
    "assets/logo.png", remote_path="/root/assets/logo.png"
)


@stub.asgi(image=image, mounts=[template_mount, asset_mount])
def fastapi_app():
    return app


# @app.post("/items/", response_model=Item)
# async def create_item(item: Item):
#     item_id = len(items) + 1
#     items[item_id] = item
#     return item


# @app.get("/items/", response_model=List[Item])
# async def read_items(skip: int = 0, limit: int = 10):
#     return list(items.values())[skip : skip + limit]


# @app.get("/items/{item_id}", response_model=Item)
# async def read_item(item_id: int):
#     item = items.get(item_id)
#     if item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return item


# @app.put("/items/{item_id}", response_model=Item)
# async def update_item(item_id: int, item: Item):
#     if item_id not in items:
#         raise HTTPException(status_code=404, detail="Item not found")
#     items[item_id] = item
#     return item


# @app.delete("/items/{item_id}", response_model=Item)
# async def delete_item(item_id: int):
#     if item_id not in items:
#         raise HTTPException(status_code=404, detail="Item not found")
#     item = items.pop(item_id)
#     return item
