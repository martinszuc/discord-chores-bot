#!/usr/bin/env python3
"""
Chores Bot - Multi-Week Simulation Test Suite
Run: cd tests && python3 test_simulation.py
"""

import json
import os
import random
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.utils.config_manager import ConfigManager
from src.utils.schedule_manager import ScheduleManager


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ChoresSimulation:
    def __init__(self, test_name, num_weeks=10):
        self.test_name = test_name
        self.num_weeks = num_weeks
        self.test_dir = Path(__file__).parent
        self.data_dir = self.test_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.setup_test_config()
        self.config_manager = ConfigManager(str(self.data_dir / "test_config.json"))
        self.schedule_manager = ScheduleManager(self.config_manager)

    def setup_test_config(self):
        test_config = {
            "token": "TEST_TOKEN",
            "prefix": "/",
            "chores_channel_id": 1234567890,
            "admin_role_id": 1234567890,
            "posting_day": "Monday",
            "posting_time": "9:00",
            "timezone": "Europe/Bratislava",
            "flatmates": [
                {"name": "Dominik", "discord_id": 111111111, "on_vacation": False,
                 "stats": {"completed": 0, "helped": 0, "reassigned": 0, "skipped": 0}},
                {"name": "Roman", "discord_id": 222222222, "on_vacation": False,
                 "stats": {"completed": 0, "helped": 0, "reassigned": 0, "skipped": 0}},
                {"name": "Jakub", "discord_id": 333333333, "on_vacation": False,
                 "stats": {"completed": 0, "helped": 0, "reassigned": 0, "skipped": 0}},
                {"name": "Denis", "discord_id": 444444444, "on_vacation": False,
                 "stats": {"completed": 0, "helped": 0, "reassigned": 0, "skipped": 0}},
                {"name": "Filip", "discord_id": 555555555, "on_vacation": False,
                 "stats": {"completed": 0, "helped": 0, "reassigned": 0, "skipped": 0}},
                {"name": "Martin", "discord_id": 666666666, "on_vacation": False,
                 "stats": {"completed": 0, "helped": 0, "reassigned": 0, "skipped": 0}}
            ],
            "chores": [
                {"name": "Kúpeľka", "frequency": 1},
                {"name": "Záchod", "frequency": 1},
                {"name": "Vysávanie a Zmývanie", "frequency": 1},
                {"name": "Vyjebat trash", "frequency": 1},
                {"name": "Vyjebat sklo", "frequency": 2}
            ],
            "emoji": {"completed": "✅", "unavailable": "❌"},
            "schedule_data_file": str(self.data_dir / "schedule_data.json"),
            "music_celebration": {"enabled": False},
            "reminders": {"enabled": False}
        }

        with open(self.data_dir / "test_config.json", 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2)

    def get_priority_score(self, flatmate_name):
        stats = self.config_manager.get_flatmate_stats(flatmate_name)
        priority = 100
        priority += stats.get("helped", 0) * 8
        priority += stats.get("completed", 0) * 3
        priority -= stats.get("skipped", 0) * 15
        priority -= stats.get("reassigned", 0) * 5
        return priority

    def print_week_header(self, week_num):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'─' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}Week {week_num}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'─' * 80}{Colors.END}")

    def print_priorities(self):
        print(f"\n{Colors.BOLD}🎯 Priorities:{Colors.END}")
        flatmates = self.config_manager.get_active_flatmates()
        priorities = []

        for flatmate in flatmates:
            name = flatmate["name"]
            stats = self.config_manager.get_flatmate_stats(name)
            priority = self.get_priority_score(name)
            priorities.append((name, priority, stats))

        priorities.sort(key=lambda x: x[1], reverse=True)

        for i, (name, priority, stats) in enumerate(priorities):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
            color = Colors.GREEN if priority > 100 else Colors.YELLOW if priority > 80 else Colors.RED
            print(f"  {medal} {color}{name:<12}{Colors.END} Priority: {color}{priority:>4}{Colors.END} "
                  f"(C:{stats['completed']} H:{stats['helped']} S:{stats['skipped']} R:{stats['reassigned']})")

    def print_assignments(self, assignments):
        print(f"\n{Colors.BOLD}📋 Assignments:{Colors.END}")
        for chore, flatmate in assignments.items():
            print(f"  • {Colors.YELLOW}{chore:<25}{Colors.END} → {Colors.GREEN}{flatmate}{Colors.END}")

    def print_stats_table(self):
        print(f"\n{Colors.BOLD}📊 Final Statistics:{Colors.END}")
        print(f"  {'Name':<12} {'Completed':>9} {'Helped':>7} {'Skipped':>7} {'Reassigned':>10} {'Priority':>9}")
        print(f"  {'-' * 12} {'-' * 9} {'-' * 7} {'-' * 7} {'-' * 10} {'-' * 9}")

        for flatmate in self.config_manager.get_flatmates():
            name = flatmate["name"]
            stats = self.config_manager.get_flatmate_stats(name)
            priority = self.get_priority_score(name)
            color = Colors.GREEN if priority > 100 else Colors.YELLOW if priority > 80 else Colors.RED
            vacation = " 🏖️" if flatmate.get("on_vacation", False) else ""

            print(f"  {color}{name:<12}{Colors.END} "
                  f"{stats['completed']:>9} {stats['helped']:>7} {stats['skipped']:>7} "
                  f"{stats['reassigned']:>10} {color}{priority:>9}{Colors.END}{vacation}")

    def simulate_week(self, week_num, completion_behavior):
        self.print_week_header(week_num)
        self.print_priorities()

        assignments = self.schedule_manager.generate_new_schedule()
        self.schedule_manager.update_last_posted_date()

        self.print_assignments(assignments)
        completion_behavior(assignments)

    def run_simulation(self, completion_behavior):
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{self.test_name:^80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.END}")

        for week in range(1, self.num_weeks + 1):
            self.simulate_week(week, completion_behavior)

        self.print_stats_table()

    def cleanup(self):
        try:
            (self.data_dir / "test_config.json").unlink(missing_ok=True)
            (self.data_dir / "schedule_data.json").unlink(missing_ok=True)
            print(f"\n{Colors.GREEN}✓ Test files cleaned up{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.YELLOW}⚠ Cleanup warning: {e}{Colors.END}")


# Test Scenarios

def test_scenario_1():
    """Everyone completes their chores"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}SCENARIO 1: Everyone Completes (10 weeks){Colors.END}")
    sim = ChoresSimulation("Scenario 1: Everyone Completes", num_weeks=10)

    def behavior(assignments):
        print(f"\n{Colors.BOLD}✅ All Complete:{Colors.END}")
        for chore, flatmate in assignments.items():
            sim.schedule_manager.mark_chore_completed(chore, flatmate)
            print(f"  ✅ {Colors.GREEN}{flatmate}{Colors.END} completed {chore}")

    sim.run_simulation(behavior)
    sim.cleanup()


def test_scenario_2():
    """Half on vacation"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}SCENARIO 2: Half On Vacation (10 weeks){Colors.END}")
    sim = ChoresSimulation("Scenario 2: Half On Vacation", num_weeks=10)

    flatmates = sim.config_manager.get_flatmates()
    for i, flatmate in enumerate(flatmates):
        if i < len(flatmates) // 2:
            sim.config_manager.set_flatmate_vacation(flatmate["name"], True)
            print(f"  🏖️ {flatmate['name']} on vacation")

    def behavior(assignments):
        print(f"\n{Colors.BOLD}✅ Active Complete:{Colors.END}")
        for chore, flatmate in assignments.items():
            sim.schedule_manager.mark_chore_completed(chore, flatmate)
            print(f"  ✅ {Colors.GREEN}{flatmate}{Colors.END} completed {chore}")

    sim.run_simulation(behavior)
    sim.cleanup()


def test_scenario_3():
    """Nobody completes anything"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}SCENARIO 3: Nobody Completes (10 weeks){Colors.END}")
    sim = ChoresSimulation("Scenario 3: Nobody Completes", num_weeks=10)

    def behavior(assignments):
        print(f"\n{Colors.BOLD}❌ All Skip:{Colors.END}")
        for chore, flatmate in assignments.items():
            new = sim.schedule_manager.randomly_reassign_chore(chore, flatmate)
            print(f"  ❌ {Colors.RED}{flatmate}{Colors.END} skipped {chore} → {Colors.YELLOW}{new}{Colors.END}")

    sim.run_simulation(behavior)
    sim.cleanup()


def test_scenario_4():
    """Mixed: 1/3 complete, 1/3 skip, 1/3 vacation"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}SCENARIO 4: Mixed Behavior (15 weeks){Colors.END}")
    sim = ChoresSimulation("Scenario 4: Mixed Behavior", num_weeks=15)

    flatmates = sim.config_manager.get_flatmates()
    third = len(flatmates) // 3
    completers = flatmates[:third]
    skippers = flatmates[third:2 * third]
    vacationers = flatmates[2 * third:]

    print(f"\n{Colors.BOLD}Groups:{Colors.END}")
    print(f"  {Colors.GREEN}Completers:{Colors.END} {', '.join([f['name'] for f in completers])}")
    print(f"  {Colors.RED}Skippers:{Colors.END} {', '.join([f['name'] for f in skippers])}")
    print(f"  {Colors.CYAN}Vacationers:{Colors.END} {', '.join([f['name'] for f in vacationers])}")

    for flatmate in vacationers:
        sim.config_manager.set_flatmate_vacation(flatmate["name"], True)

    def behavior(assignments):
        print(f"\n{Colors.BOLD}📝 Actions:{Colors.END}")
        for chore, flatmate in assignments.items():
            flatmate_obj = sim.config_manager.get_flatmate_by_name(flatmate)

            if flatmate_obj in completers:
                sim.schedule_manager.mark_chore_completed(chore, flatmate)
                print(f"  ✅ {Colors.GREEN}{flatmate}{Colors.END} completed {chore}")
            elif flatmate_obj in skippers:
                new = sim.schedule_manager.randomly_reassign_chore(chore, flatmate)
                print(f"  ❌ {Colors.RED}{flatmate}{Colors.END} skipped → {Colors.YELLOW}{new}{Colors.END}")
                if new:
                    sim.schedule_manager.mark_chore_completed(chore, flatmate, helper=new)
                    print(f"     ✅ {Colors.GREEN}{new}{Colors.END} helped")

    sim.run_simulation(behavior)
    sim.cleanup()


def test_scenario_5():
    """Random chaos"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}SCENARIO 5: Random Chaos (15 weeks){Colors.END}")
    sim = ChoresSimulation("Scenario 5: Random Chaos", num_weeks=15)

    def behavior(assignments):
        print(f"\n{Colors.BOLD}🎲 Random:{Colors.END}")
        for chore, flatmate in assignments.items():
            action = random.choice(["complete"] * 4 + ["help"] * 3 + ["skip"] * 2 + ["late"])

            if action == "complete":
                sim.schedule_manager.mark_chore_completed(chore, flatmate)
                print(f"  ✅ {Colors.GREEN}{flatmate}{Colors.END} completed {chore}")
            elif action == "help":
                helpers = [f["name"] for f in sim.config_manager.get_active_flatmates() if f["name"] != flatmate]
                if helpers:
                    helper = random.choice(helpers)
                    sim.schedule_manager.mark_chore_completed(chore, flatmate, helper=helper)
                    print(f"  🦸 {Colors.CYAN}{helper}{Colors.END} helped {flatmate}")
            elif action == "skip":
                new = sim.schedule_manager.randomly_reassign_chore(chore, flatmate)
                print(f"  ❌ {Colors.RED}{flatmate}{Colors.END} skipped → {Colors.YELLOW}{new}{Colors.END}")
                if new:
                    sim.schedule_manager.mark_chore_completed(chore, flatmate, helper=new)

    sim.run_simulation(behavior)
    sim.cleanup()


def run_all_tests():
    """Run all 5 test scenarios"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║              CHORES BOT - RUNNING ALL TEST SCENARIOS                      ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")

    test_scenario_1()
    input(f"\n{Colors.BOLD}Press Enter for next test...{Colors.END}")

    test_scenario_2()
    input(f"\n{Colors.BOLD}Press Enter for next test...{Colors.END}")

    test_scenario_3()
    input(f"\n{Colors.BOLD}Press Enter for next test...{Colors.END}")

    test_scenario_4()
    input(f"\n{Colors.BOLD}Press Enter for next test...{Colors.END}")

    test_scenario_5()

    print(f"\n{Colors.BOLD}{Colors.GREEN}✓ All tests complete!{Colors.END}\n")


if __name__ == "__main__":
    run_all_tests()