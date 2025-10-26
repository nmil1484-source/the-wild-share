#!/bin/bash
set -e

echo "Building frontend..."
cd rental-site

# Install dependencies
echo "Installing frontend dependencies..."
pnpm install

# Set environment variables for build
export VITE_STRIPE_PUBLISHABLE_KEY="${STRIPE_PUBLISHABLE_KEY}"

# Build the React app
echo "Building React app..."
pnpm run build

# Copy built files to backend static folder
echo "Copying built files to backend..."
rm -rf ../backend/src/static/*
cp -r dist/* ../backend/src/static/

echo "Frontend build complete!"
cd ..

