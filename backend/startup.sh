# Run upgrade before running server
alembic upgrade head

# Start Flask Server
flask --app main run --host 0.0.0.0 