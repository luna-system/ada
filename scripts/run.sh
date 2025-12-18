#!/bin/bash
# Helper script for running Ada utility scripts via Docker container
# Usage: ./run.sh <command>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# If repository uses Nix flakes, try to update flake.lock to refresh any outdated inputs
if [ -f flake.lock ]; then
    echo -e "${BLUE}🔄 flake.lock detected — attempting to update to refresh inputs...${NC}"
    if command -v nix >/dev/null 2>&1; then
        # Try the more explicit recreate option first (newer nix)
        if nix flake update --recreate-lock-file 2>/dev/null; then
            echo -e "${GREEN}✓ flake.lock recreated successfully${NC}"
        else
            # Fallback to basic update for older nix versions
            if nix flake update 2>/dev/null; then
                echo -e "${GREEN}✓ flake.lock updated successfully${NC}"
            else
                echo -e "${YELLOW}⚠️  nix flake update failed — continuing without updating flake.lock${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  nix not found in PATH — skipping flake.lock update${NC}"
    fi
    echo ""
fi

show_help() {
    echo -e "${BLUE}Ada Scripts Runner${NC}"
    echo ""
    echo "Usage: ./scripts/run.sh <command>"
    echo ""
    echo "Commands:"
    echo "  health           Run health check"
    echo "  test             Run pytest test suite"
    echo "  test-legacy      Run old test_prompt_interface.py"
    echo "  migrate          Run Chroma migration"
    echo "  consolidate      Run memory consolidation"
    echo "  import-faq       Import FAQs from seed data"
    echo "  import-turns     Import turns from CSV"
    echo "  load-persona     Load persona into Chroma"
    echo "  shell            Start interactive Python shell"
    echo "  bash             Start bash shell in container"
    echo "  <script.py>      Run custom script from scripts/ directory"
    echo ""
    echo "Examples:"
    echo "  ./scripts/run.sh health"
    echo "  ./scripts/run.sh test"
    echo "  ./scripts/run.sh my_custom_script.py"
}

run_command() {
    local cmd="$1"
    case "$cmd" in
        health)
            echo -e "${BLUE}Running health check...${NC}"
            docker compose run --rm scripts python /app/scripts/health_check_chroma.py
            ;;
        test)
            echo -e "${BLUE}Running test suite...${NC}"
            docker compose run --rm scripts pytest
            ;;
        test-legacy)
            echo -e "${BLUE}Running legacy test suite...${NC}"
            docker compose run --rm scripts python /app/scripts/test_prompt_interface.py
            ;;
        migrate)
            echo -e "${YELLOW}⚠️  Running Chroma migration (creates backup and re-embeds all documents)${NC}"
            read -p "Continue? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker compose run --rm scripts python /app/scripts/migrate_chroma_http.py
            else
                echo "Cancelled"
            fi
            ;;
        consolidate)
            echo -e "${BLUE}Running memory consolidation...${NC}"
            docker compose run --rm scripts python /app/scripts/consolidate_memories.py
            ;;
        import-faq)
            echo -e "${BLUE}Importing FAQs...${NC}"
            docker compose run --rm scripts python /app/scripts/import_faq.py
            ;;
        import-turns)
            echo -e "${BLUE}Importing turns from CSV...${NC}"
            docker compose run --rm scripts python /app/scripts/import_turns_csv.py
            ;;
        load-persona)
            echo -e "${BLUE}Loading persona...${NC}"
            docker compose run --rm scripts python /app/scripts/load_persona.py
            ;;
        shell)
            echo -e "${BLUE}Starting interactive Python shell...${NC}"
            docker compose run --rm scripts python
            ;;
        bash)
            echo -e "${BLUE}Starting bash shell...${NC}"
            docker compose run --rm scripts bash
            ;;
        *.py)
            echo -e "${BLUE}Running custom script: $cmd${NC}"
            docker compose run --rm scripts python "/app/scripts/$cmd"
            ;;
        *)
            echo -e "${YELLOW}Unknown command: $cmd${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Main
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

run_command "$1"
