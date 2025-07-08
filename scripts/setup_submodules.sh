#!/bin/bash
# Setup script for Memra SDK submodules with sparse checkout
# This script configures shallow, sparse submodules for minimal download

set -e

echo "🔧 Setting up Memra SDK submodules with sparse checkout..."

# Function to setup sparse checkout for a submodule
setup_sparse_checkout() {
    local submodule_path=$1
    local sparse_paths=$2
    
    if [ -d "$submodule_path/.git" ]; then
        echo "📁 Setting up sparse checkout for $submodule_path"
        
        # Enable sparse checkout
        cd "$submodule_path"
        git config core.sparseCheckout true
        
        # Clear existing sparse-checkout file and add new paths
        rm -f .git/info/sparse-checkout
        for path in $sparse_paths; do
            echo "$path" >> .git/info/sparse-checkout
        done
        
        # Reset to apply sparse checkout
        git read-tree -m -u HEAD
        
        cd ..
        echo "✅ Sparse checkout configured for $submodule_path"
    else
        echo "⚠️  Warning: $submodule_path is not a git repository"
    fi
}

# Setup memra-ops sparse checkout (minimal files for ETL demo)
setup_sparse_checkout "memra-ops" "docker-compose.yml docker-compose.mcp.yml Dockerfile.mcp mcp_bridge_server.py requirements.txt"

# Setup memra-workflows sparse checkout (workflow templates)
setup_sparse_checkout "memra-workflows" "invoice_processing/ accounts_payable/ propane_delivery/ text_to_sql/"

echo "🎉 Submodule setup complete!"
echo ""
echo "📋 What you have access to:"
echo "  • memra-ops/: Docker Compose files and MCP bridge server"
echo "  • memra-workflows/: Production workflow templates"
echo ""
echo "💡 To get full access to all files, run:"
echo "  git -C memra-ops sparse-checkout disable"
echo "  git -C memra-workflows sparse-checkout disable" 