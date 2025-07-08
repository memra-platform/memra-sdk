#!/bin/bash

echo "🚀 Setting up Memra ETL Dashboard..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm found"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create environment file
echo "🔧 Creating environment file..."
cat > .env.local << EOF
NEXT_PUBLIC_MEMRA_API_URL=https://api.memra.co
EOF

echo "✅ Environment file created"

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
/coverage

# Next.js
/.next/
/out/

# Production
/build

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env*.local

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts
EOF
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start development server: npm run dev"
echo "2. Open http://localhost:3000"
echo "3. Enter your Memra API key"
echo "4. Upload and process invoices!"
echo ""
echo "🚀 To deploy to Vercel:"
echo "1. Install Vercel CLI: npm i -g vercel"
echo "2. Deploy: vercel"
echo "3. Follow the prompts" 