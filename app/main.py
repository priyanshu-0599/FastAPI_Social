import sys

sys.path.append(".")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app import model
from app.database import engine
from app.routers import post, user, auth, vote

# model.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to my API"}


app.include_router(router=auth.router)
app.include_router(router=post.router)
app.include_router(router=user.router)
app.include_router(router=vote.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
