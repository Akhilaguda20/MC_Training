from dotenv import load_dotenv
load_dotenv()  # loads .env before any router imports

from fastapi import FastAPI
from update_user.router import router as update_user_router
from create_user.router import router as create_user_router
from delete_user.router import router as delete_user_router
from get_user.router import router as get_user_router 

app = FastAPI()
app.include_router(create_user_router)
app.include_router(get_user_router)
app.include_router(update_user_router)
app.include_router(delete_user_router)
