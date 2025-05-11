#!/bin/bash

echo "Checking database connection..."
python -c "
import sys
from sqlalchemy import create_engine
from app.core.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    connection = engine.connect()
    connection.close()
    print('Database connection successful!')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "Database is configured correctly."
    echo "Run 'alembic revision --autogenerate -m \"create tables\"' to create migration scripts."
    echo "Then run 'alembic upgrade head' to apply migrations."
else
    echo "Please check your database configuration in .env file."
fi
