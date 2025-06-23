#!/bin/bash

# Create .env.local file if it doesn't exist
if [ ! -f "client/Frontend/next-theme-setup (1)/.env.local" ]; then
    echo "Creating .env.local file..."
    cat > "client/Frontend/next-theme-setup (1)/.env.local" << EOL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
EOL
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "client/Frontend/next-theme-setup (1)/node_modules" ]; then
    echo "Installing dependencies..."
    cd "client/Frontend/next-theme-setup (1)" && npm install
    cd ../../..
fi

# Start the Next.js development server
echo "Starting Next.js development server..."
cd "client/Frontend/next-theme-setup (1)" && npm run dev 