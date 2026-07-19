#!/bin/bash

# 1. Create the base folders
mkdir -p thinking-os/{apps,python/thinkingos/src/thinkingos,docs,examples,benchmarks,tests}
cd thinking-os

# 2. Create the root documentation files
touch README.md ARCHITECTURE.md ROADMAP.md CONTRIBUTING.md

# 3. Create the Rust Core Crates (Libraries)
mkdir crates
for crate in semantic-ir ontology parser storage graph query-engine search embeddings reasoning ai plugin-api mcp-server; do
    cargo new --lib crates/$crate
done

# 4. Create the CLI Application (Binary)
cargo new --bin apps/cli

# 5. Scaffold the TypeScript/JS Frontends
for app in obsidian-plugin web-dashboard vscode-extension; do
    mkdir -p apps/$app/src
    echo "{\"name\": \"$app\", \"version\": \"0.1.0\"}" > apps/$app/package.json
    echo "# $app" > apps/$app/README.md
done

# 6. Scaffold the Python SDK
touch python/thinkingos/pyproject.toml
touch python/thinkingos/src/thinkingos/__init__.py

# 7. Create the Top-Level Cargo Workspace
cat << 'EOF' > Cargo.toml
[workspace]
resolver = "2"
members = [
    "apps/cli",
    "crates/*"
]

[workspace.package]
version = "0.1.0"
authors = ["Your Name <you@example.com>"]
edition = "2021"

[profile.dev.package."*"]
opt-level = 3

[profile.release]
lto = true
codegen-units = 1
EOF

# 8. Initialize git repository
git init
echo "/target" > .gitignore
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.db" >> .gitignore

echo "🚀 ThinkingOS Monorepo successfully initialized!"
