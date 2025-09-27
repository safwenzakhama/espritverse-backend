@echo off
echo 🚀 Starting EspritVerse Development Environment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose is not installed. Please install docker-compose and try again.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy env.example .env
    echo ⚠️  Please edit .env file with your actual values before continuing.
    echo    Especially set your GEMINI_API_KEY and SECRET_KEY
    pause
)

REM Build and start containers
echo 🔨 Building and starting containers...
docker-compose up --build -d

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM Run migrations
echo 🗄️  Running database migrations...
docker-compose exec web python manage.py migrate

REM Create superuser if it doesn't exist
echo 👤 Creating superuser (if needed)...
docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>nul || echo Superuser already exists or creation failed

REM Collect static files
echo 📦 Collecting static files...
docker-compose exec web python manage.py collectstatic --noinput

echo ✅ EspritVerse is now running!
echo 🌐 Backend: http://localhost:8000
echo 📊 Admin: http://localhost:8000/admin
echo 📚 API Docs: http://localhost:8000/api/schema/swagger-ui/
echo.
echo To stop the services, run: docker-compose down
echo To view logs, run: docker-compose logs -f
pause
