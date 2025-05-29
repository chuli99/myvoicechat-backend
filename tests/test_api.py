import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_URL = (f'postgresql://postgres:{DATABASE_PASSWORD}@localhost:5432/myvoicedb')


print(DATABASE_PASSWORD)
print(DATABASE_URL)  