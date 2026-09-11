#!/usr/bin/env bash
set -e

# ============================================================
# OneHive Digital Presence Intelligence Engine
# Quick Start Launcher
# ============================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

echo "============================================================"
echo "ONEHIVE TECHNOLOGIES — DIGITAL PRESENCE INTELLIGENCE"
echo "Starting OneHive Digital Growth Pack Engine..."
echo "============================================================"

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/backend/storage/artifacts/reports"
mkdir -p "$PROJECT_ROOT/backend/storage/artifacts/previews"
mkdir -p "$PROJECT_ROOT/backend/storage/artifacts/quickwins"
mkdir -p "$PROJECT_ROOT/backend/storage/artifacts/salespacks"

# 1. Start Backend FastAPI on port 8050
echo "[1/2] Starting Backend FastAPI Server on http://127.0.0.1:8050..."
cd "$PROJECT_ROOT"
PYTHONPATH=backend backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8050 --reload &
BACKEND_PID=$!

# 2. Start Frontend Next.js on port 3001
echo "[2/2] Starting Frontend Next.js Server on http://localhost:3001..."
cd "$PROJECT_ROOT/frontend"
npm run dev -- -p 3001 &
FRONTEND_PID=$!

echo "============================================================"
echo "OneHive Engine is ACTIVE:"
echo "• Dashboard: http://localhost:3001"
echo "• API Docs:  http://127.0.0.1:8050/docs"
echo "• Press Ctrl+C to terminate both servers."
echo "============================================================"

cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM
wait
