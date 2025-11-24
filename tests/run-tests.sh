#!/bin/bash

# Chores Bot - Test Suite Runner
# Makes it easy to run the simulation tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                 CHORES BOT - TEST SUITE RUNNER                             ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Check if test file exists
if [ ! -f "test_simulation.py" ]; then
    echo -e "${RED}Error: test_simulation.py not found!${NC}"
    echo -e "${YELLOW}Please copy it from /tmp/test_simulation.py${NC}"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
required_version="3.8"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo -e "${RED}Error: Python $required_version or higher required${NC}"
    echo -e "${YELLOW}Current version: $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $python_version detected${NC}\n"

# Function to run a specific scenario
run_scenario() {
    local scenario=$1
    local name=$2

    echo -e "\n${BOLD}${CYAN}Running: $name${NC}\n"
    echo "$scenario" | python3 test_simulation.py

    echo -e "\n${BOLD}Press Enter to continue...${NC}"
    read
}

# Menu
echo -e "${BOLD}Quick Test Options:${NC}\n"
echo -e "  ${CYAN}1.${NC} Scenario 1: Everyone Completes (10 weeks)"
echo -e "  ${CYAN}2.${NC} Scenario 2: Half On Vacation (10 weeks)"
echo -e "  ${CYAN}3.${NC} Scenario 3: Nobody Completes (10 weeks)"
echo -e "  ${CYAN}4.${NC} Scenario 4: Mixed Behavior (15 weeks) ${GREEN}← RECOMMENDED${NC}"
echo -e "  ${CYAN}5.${NC} Scenario 5: Random Chaos (15 weeks)"
echo -e "  ${CYAN}A.${NC} Run All Scenarios"
echo -e "  ${CYAN}I.${NC} Interactive Mode (choose in program)"
echo -e "  ${CYAN}Q.${NC} Quit"

echo -ne "\n${BOLD}Select option (1-5, A, I, or Q): ${NC}"
read choice

case $choice in
    1)
        run_scenario "1" "Scenario 1: Everyone Completes"
        ;;
    2)
        run_scenario "2" "Scenario 2: Half On Vacation"
        ;;
    3)
        run_scenario "3" "Scenario 3: Nobody Completes"
        ;;
    4)
        run_scenario "4" "Scenario 4: Mixed Behavior"
        ;;
    5)
        run_scenario "5" "Scenario 5: Random Chaos"
        ;;
    [Aa])
        echo -e "\n${BOLD}${YELLOW}Running all scenarios...${NC}\n"
        echo "A" | python3 test_simulation.py
        ;;
    [Ii])
        python3 test_simulation.py
        ;;
    [Qq])
        echo -e "${YELLOW}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option!${NC}"
        exit 1
        ;;
esac

# Cleanup info
echo -e "\n${GREEN}✓ Test complete!${NC}"
echo -e "${CYAN}All temporary test files have been cleaned up.${NC}"
echo -e "${YELLOW}Your production config and data are unchanged.${NC}\n"