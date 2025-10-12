#!/bin/bash
set -e

echo "🚀 Starting Brody Backend..."

# Initialize database if needed
if [ "$DATABASE_URL" ]; then
    echo "📦 Initializing database..."
    python3 -c "from database import Base, engine; Base.metadata.create_all(engine)" || echo "⚠️  Database initialization skipped (may already exist)"
fi

# Start the server
echo "🌐 Starting FastAPI server on 0.0.0.0:${PORT:-9000}..."
exec python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-9000} --log-level info
