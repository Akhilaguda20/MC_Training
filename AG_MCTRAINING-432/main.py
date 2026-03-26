import os
import sys

from dotenv import load_dotenv
load_dotenv() 

# Lambda extracts zip to /var/task — dependencies/ is a subfolder, not on sys.path by default
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dependencies"))
from fastapi import FastAPI
from mangum import Mangum


from update_user.router import router as update_user_router
from create_user.router import router as create_user_router
from delete_user.router import router as delete_user_router
from get_user.router import router as get_user_router 

app = FastAPI()

app.include_router(create_user_router)
app.include_router(get_user_router)
app.include_router(update_user_router)
app.include_router(delete_user_router)

handler = Mangum(app)