# Multiplayer Architecture - Team Fire Response System

## Overview

The Wildfire CLI multiplayer system enables teams to coordinate wildfire incident response through Discord guilds. Each guild channel can host a single active fire incident with multiple team members collaborating in real-time.

## Core Architecture

### Fire Management System

#### Guild Fire Creation
- **Location**: `WildfireGame.create_fire(channel_id)`
- **Features**: 
  - One active fire per Discord channel
  - Full `FireGrid` simulation engine (cellular automata)
  - Real weather conditions and terrain modeling
  - Auto-progression every 45 seconds
  - Shared team budget ($50k starting)

#### Fire Data Structure
```python
guild_fire = {
    "id": "guild_fire_{channel_id}_{timestamp}",
    "channel_id": channel_id,
    "fire_grid": FireGrid(),  # Full simulation engine
    "weather": WeatherConditions(),
    "responders": [],  # Team member list
    "resources_deployed": {"hand_crews": 0, "engines": 0, "air_tankers": 0, "dozers": 0},
    "team_budget": 50,  # Shared budget in thousands
    "next_progression": datetime,  # Auto-progression timing
    "status": "active",  # active, contained, critical_failure
    "incident_name": "Guild Fire XXXX"
}
```

### Team Coordination System

#### Player Assignment
- **Command**: `/respond` in guild channel
- **Function**: `WildfireGame.assign_player(fire_id, player_id, name)`
- **Behavior**: Players join team responder list for coordination

#### Shared Resource Deployment
- **System**: `WildfireGame.deploy_team_resources(fire_id, player_id, resource_type, count)`
- **Budget**: Shared team budget with real-time deduction
- **Coordination**: All team members see resource deployments immediately
- **Resource Types**:
  - Ground Crews: $2k (fast attack, all terrain)
  - Engines: $3k (structure protection, balanced)
  - Air Support: $5k (heavy suppression power)
  - Dozers: $4k (fire line construction)

### Real-time Progression System

#### Auto-Progression Loop
- **Frequency**: Every 45 seconds for active guild fires
- **Process**:
  1. Apply suppression from deployed team resources
  2. Advance fire simulation (weather, spread, containment)
  3. Calculate team performance bonuses/penalties
  4. Update shared team budget
  5. Send team-wide notifications to guild channel

#### Team Budget Economy
- **Earning Budget**: Teams earn budget through good fire containment
  - Excellent coordination: +$12k budget
  - Good progress: +$8k budget  
  - Some progress: +$5k budget
  - Minimal progress: +$2k budget
- **Losing Budget**: Fire growth reduces team budget
  - Significant growth (>30 acres): -$4k budget
  - Some growth (>15 acres): -$2k budget

### User Interface Components

#### Team Tactical Choices (`TeamTacticalChoicesView`)
- **Interactive Buttons**: Click-to-deploy resource options
- **Real-time Feedback**: Immediate suppression effects and budget updates  
- **Team Visibility**: All deployments visible to entire team
- **Auto-progression Integration**: Shows progression results when triggered

#### Team Status Updates
- **Automatic Notifications**: Sent to guild channel every 45 seconds
- **Progress Indicators**: Fire size change, containment improvement
- **Team Performance**: Budget earned/lost, coordination feedback
- **Mission Status**: Win/lose conditions with team celebration/lessons

## Command Flow Patterns

### Guild vs DM Detection
```python
@discord.app_commands.command(name="fire")
async def fire_command(self, interaction: discord.Interaction):
    if interaction.guild is None:
        await self._handle_singleplayer_fire(interaction)  # DM mode
    else:
        await self._handle_multiplayer_fire(interaction)   # Guild mode
```

### Team Fire Workflow
1. **Fire Creation**: `/fire` in guild channel → New team incident
2. **Team Assembly**: Multiple users `/respond` → Join team responders
3. **Resource Deployment**: Team members use interactive buttons → Deploy resources
4. **Auto-Progression**: Background system → 45-second fire progression
5. **Team Updates**: Automatic notifications → Team-wide status updates
6. **Mission Completion**: 100% containment or >200 acres → Team success/failure

## Integration Points

### Discord Bot Commands
- **Context-Aware**: Same commands work in DM (singleplayer) and Guild (multiplayer)
- **Channel-Specific**: Each guild channel can have one active fire
- **Real-time Updates**: Background task system sends team notifications

### Fire Simulation Engine
- **Shared Engine**: Uses same `FireGrid` system as singleplayer
- **Team Resources**: Aggregates multiple team member resource deployments
- **Performance Calculation**: Team-based scoring vs individual scoring

### Database/State Management
- **In-Memory**: Current implementation uses in-memory state
- **Persistence**: Fire state persists across bot restarts via auto-progression timing
- **Scalability**: Supports multiple concurrent guild fires across servers

## Testing Scenarios

### 2-User Team Coordination
```
User A: /fire → Creates incident in #wildfire-response
User B: /respond → Joins team for incident
User A: [Deploys Ground Crews $2k]
User B: [Deploys Air Support $5k] 
System: [Auto-progression every 45s with team updates]
Team: [Coordinate to reach 100% containment]
```

### Resource Conflict Resolution
- **Budget Sharing**: Team budget prevents overspending
- **Deployment Visibility**: All team members see current resource allocation
- **Coordination Incentive**: Team budget bonuses encourage coordination

### Performance Metrics
- **Team Success Rate**: Percentage of incidents contained by teams
- **Budget Efficiency**: Team budget usage vs fire containment success
- **Coordination Quality**: Team resource deployment timing and effectiveness

## Future Enhancement Opportunities

### Role-Based Coordination
- **Incident Commander**: Strategic oversight and resource allocation
- **Operations Chief**: Tactical resource deployment
- **Planning Chief**: Weather analysis and strategic planning
- **Logistics Chief**: Resource availability and supply coordination

### Inter-Agency Coordination
- **Multi-Guild Incidents**: Large fires requiring multiple Discord servers
- **Resource Sharing**: Teams can request/provide mutual aid
- **Unified Command**: Joint incident command across organizations

### Advanced Team Features
- **Voice Integration**: Discord voice channel coordination during incidents
- **Real-time Maps**: Shared tactical situation awareness
- **Training Scenarios**: Structured team training exercises
- **Performance Analytics**: Detailed team coordination metrics

---

**Architecture Status**: ✅ **IMPLEMENTED AND OPERATIONAL**

The multiplayer architecture provides a solid foundation for team-based wildfire incident command training with real-time coordination, shared resource management, and authentic incident command protocols.