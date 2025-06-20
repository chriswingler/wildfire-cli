# Developer Onboarding Guide

Welcome to the Wildfire Bot project! This guide will help you get started with understanding the project structure, setting up your environment, and contributing to the codebase.

## 1. Project Overview

The Wildfire Bot is a Discord-based game simulating wildfire incidents and response. It features:
*   A fire simulation engine using cellular automata.
*   Discord slash commands for user interaction.
*   Single-player and multiplayer (team-based) modes.
*   Persistence of game data using SQLite.

**Key Architectural Decisions**:
To understand the foundational decisions behind the bot's architecture, please review our Architecture Decision Records (ADRs):
*   [ADR-001: Choice of Discord as Primary Interface](./adr/ADR-001-discord-interface.md)
*   [ADR-002: Use of Cellular Automata for Fire Simulation](./adr/ADR-002-cellular-automata-simulation.md)
*   [ADR-003: SQLite for Database Storage](./adr/ADR-003-sqlite-database.md)
*   [ADR-004: In-Memory State for Active Multiplayer Fire Sessions](./adr/ADR-004-in-memory-multiplayer-state.md)

## 2. Getting Started

### Prerequisites
*   Python 3.8 or higher
*   Git
*   A Discord account and a test server where you can add your bot instance.

### Setup Instructions

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a Virtual Environment**:
    It's highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    You may also need development tools for documentation:
    ```bash
    pip install sphinx sphinx-autodoc-typehints napoleon
    ```

4.  **Configure Environment Variables**:
    *   Create a `.env` file in the root directory of the project by copying `.env.example` (if it exists, otherwise create it from scratch).
    *   Add your Discord Bot Token to the `.env` file:
        ```
        DISCORD_TOKEN=your_bot_token_here
        ```
    *   You can obtain a bot token by creating a new application on the [Discord Developer Portal](https://discord.com/developers/applications).

5.  **Run the Bot**:
    ```bash
    python src/main.py
    ```
    The bot should connect to Discord and be ready for commands on your test server (once invited).

## 3. Codebase Structure

*   `src/`: Contains the main source code for the bot.
    *   `main.py`: Main entry point for the bot.
    *   `commands.py`: Defines Discord slash commands and core game logic related to user interactions and database state for simple fires.
    *   `fire_engine.py`: Implements the cellular automata based fire simulation engine.
    *   `discord_wildfire.py`: Contains setup logic for commands and potentially more complex game interactions (integrates with `fire_engine.py`).
    *   `utilities.py`: Helper functions and classes.
    *   `ui/`: Components related to user interface elements like embeds.
*   `docs/`: Contains all documentation files.
    *   `api/`: Generated API documentation.
    *   `adr/`: Architecture Decision Records.
    *   Other markdown files detailing specific systems.
*   `.github/`: GitHub-specific files, including workflow definitions for CI/CD.
*   `requirements.txt`: Python dependencies.
*   `wildfire_game.db`: SQLite database file (will be created on first run if it doesn't exist).

## 4. Key Systems Documentation

To understand the core components of the bot, refer to the following documents:

*   **API Documentation (Bot Commands)**:
    *   The primary API documentation for bot commands is generated using Sphinx from docstrings in `src/commands.py`.
    *   To generate and view this documentation locally:
        1.  Navigate to the `docs/` directory.
        2.  Run `sphinx-build -b html . _build` (or `make html` if a Makefile exists).
        3.  Open `_build/html/index.html` in your browser.
    *   This documentation details all slash commands, their parameters, and usage.

*   **Fire Simulation Engine**:
    *   [Fire Simulation Algorithm](./fire-simulation-algorithm.md): Explains the cellular automata model, fire spread mechanics, weather effects, and suppression logic.

*   **Database**:
    *   [Database Schema and Data Flow](./database-schema.md): Details the SQLite database structure, tables (`fires`, `responders`), and how data is managed.

*   **Multiplayer Architecture**:
    *   [Multiplayer Architecture](./multiplayer-architecture.md): Describes the system for team-based fire response, including shared state and real-time progression. (This document was pre-existing and is a key resource).

## 5. Development Guidelines

*   **Coding Standards**: Please refer to `docs/coding_standards.md` (if this file exists, otherwise assume PEP 8).
*   **Branching**: Use feature branches for new development (e.g., `feature/my-new-feature`). Create pull requests to merge into the main branch.
*   **Commits**: Write clear and concise commit messages.
*   **Testing**: Refer to `docs/debug-testing-guide.md` and `docs/multiplayer-testing-guide.md` for testing practices. (These files were pre-existing).
*   **Documentation**:
    *   Keep docstrings in Python code up-to-date, especially for public APIs and complex logic. These are used for Sphinx documentation.
    *   For significant new features or changes to architecture, consider if a new ADR or an update to existing documentation is necessary.

## 6. Contribution Process

1.  Pick an issue or discuss a new feature/bug fix.
2.  Create a new branch from the latest `main` (or `develop` if used).
3.  Implement your changes, including tests and documentation.
4.  Ensure your code passes any linting or quality checks (see CI/CD workflows).
5.  Submit a Pull Request (PR) for review.
6.  Address any feedback from reviewers.
7.  Once approved, your PR will be merged.

Happy coding!
