#!/bin/bash

echo "🛑 Stopping AI Language Learning Platform..."

# Kill processes on our ports
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "✅ Services stopped" 