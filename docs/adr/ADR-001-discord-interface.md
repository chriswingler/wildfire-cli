# ADR-001: Choice of Discord as Primary Interface

*   **Status**: Accepted
*   **Date**: 2024-07-23
*   **Deciders**: Project Originators

## Context

The project aims to create an interactive wildfire simulation game that allows for both single-player and multi-player team-based experiences. A platform is needed that supports text-based commands, real-time updates, user authentication, and community building.

## Decision

Discord will be used as the primary interface for the Wildfire Bot. This includes:
*   Slash commands for user interactions.
*   Text channels for game instances and updates.
*   Guilds (servers) for organizing player groups and multiplayer games.
*   Bot accounts for game logic and communication.

## Consequences

**Positive**:
*   **Wide Adoption**: Discord is a popular platform, especially within gaming communities, lowering the barrier to entry for users.
*   **Rich API**: Discord provides a robust API (discord.py, discord.js) for bot development, supporting slash commands, embeds, buttons, and real-time events.
*   **Built-in User Management**: Handles user accounts, roles, and permissions.
*   **Real-time Communication**: Native support for instant messaging and notifications, crucial for game updates.
*   **Community Features**: Guilds, channels, and roles facilitate community building around the game.
*   **Free Hosting (for users)**: Users can easily create or join servers without cost. Bot hosting is separate.
*   **Mobile and Desktop Access**: Users can interact with the bot from various devices.

**Negative**:
*   **Rate Limiting**: Bot actions are subject to Discord API rate limits, which can affect responsiveness if not managed carefully.
*   **Dependency on Discord**: Any Discord outages or API changes can impact the bot's availability and functionality.
*   **Not a Dedicated Gaming Platform**: While popular for gaming communities, Discord is not a specialized game hosting platform. Complex UIs or graphical elements are limited.
*   **Text-Based Interaction Model**: Gameplay is primarily text-based, which might not appeal to all users. Visualizations are limited to embeds and simple grid representations.
*   **Learning Curve for Discord API**: Developers need to be familiar with `discord.py` or similar libraries.
