import uvicorn
from fastapi import FastAPI
from database import engine, Base
from routers.user_actions import router
from auth import auth
from starlette.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(auth.router)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, workers=3)
