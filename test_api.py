import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")   
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_ROUTE = os.getenv("DATABASE_ROUTE")

print(DATABASE_URL)  
print(DATABASE_PASSWORD)
print(DATABASE_ROUTE)
