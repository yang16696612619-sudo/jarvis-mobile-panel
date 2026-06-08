@echo off
REM ============================================================
REM Deploy Jarvis Mobile Web to Railway
REM ============================================================
echo [1/4] Checking Railway CLI...
where railway >nul 2>&1 || (
  echo Installing Railway CLI...
  npm install -g @railway/cli
)

echo [2/4] Checking login...
railway whoami >nul 2>&1 || (
  echo Please login to Railway.
  echo A browser window will open -- log in with your Railway account.
  railway login
)

echo [3/4] Initializing Railway project...
railway init --name jarvis-mobile-panel

echo [4/4] Deploying to Railway...
railway up --detach

echo.
echo ============================================================
echo Deployment initiated! Run the following to get your URL:
echo   railway status
echo.
echo Then set your PUSH_TOKEN:
echo   railway variables set PUSH_TOKEN=your-random-token-here
echo ============================================================
pause
