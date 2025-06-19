# Debug Testing Guide - Single Account Multiplayer Testing

## ⚡ **QUICK START (30 seconds)**

1. **Go to any Discord guild channel**
2. **Run: `/fire`** → Creates team fire with auto-progression
3. **Run: `/respond`** → Join as Player 1, get deployment buttons
4. **Run: `/debugplayer2`** → Add simulated Player 2 to team
5. **Click button or run: `/debugp2deploy resource:hand_crews`** → Player 2 deploys
6. **Wait 45 seconds** → Watch automatic team update message!

## 🧪 **DEBUG COMMANDS ADDED**

I've added special debug commands that let you simulate Player 2 from your single Discord account to test multiplayer coordination:

### **Debug Commands (Guild channels only):**
- **`/debugplayer2`** - Simulate Player 2 joining your team
- **`/debugp2deploy`** - Deploy resources as Player 2  
- **`/debugstatus`** - Show detailed multiplayer debug info
- **`/debugclear`** - Clear all guild fires for fresh testing

## 🎮 **COMPLETE TESTING WORKFLOW**

### **Step 1: Create Team Fire**
```
1. Go to any Discord guild channel
2. Run: /fire
3. Result: Team incident created with auto-progression
```

### **Step 2: Join as Player 1**
```
1. Run: /respond
2. Result: You join as Player 1 with deployment buttons
3. Deploy resources using interactive buttons (1 🚒, 2 🚁, 3 🚛, 4 🚜)
```

### **Step 3: Add Simulated Player 2**
```
1. Run: /debugplayer2  
2. Result: "YourName-Player2" joins the team
3. Now you have 2 team members for testing
```

### **Step 4: Test Team Coordination**
```
1. Deploy as Player 1: Use interactive buttons
2. Deploy as Player 2: /debugp2deploy resource:hand_crews count:1
3. Check team status: /firestatus or /debugstatus
4. Watch auto-progression: Every 45 seconds you'll get team updates
```

### **Step 5: Observe Team Features**
```
✅ Shared team budget ($50k starting)
✅ Real-time team notifications every 45 seconds  
✅ Team resource visibility (both players see all deployments)
✅ Team performance bonuses/penalties
✅ Mission success/failure for team coordination
```

## 🎯 **TESTING SCENARIOS**

### **Budget Coordination Test**
```
1. /fire → Create incident ($50k team budget)
2. /respond → Join as Player 1
3. Deploy Air Support (costs $5k) → Budget: $45k
4. /debugplayer2 → Add Player 2
5. /debugp2deploy resource:air_tankers → Player 2 deploys Air Support ($5k) → Budget: $40k
6. /firestatus → Verify both deployments visible
```

### **Auto-Progression Test**
```
1. Create fire and add Player 2
2. Deploy some resources from both players
3. Wait 45 seconds
4. Observe: Team update message appears automatically
5. Check if team earned budget for good coordination
```

### **Resource Coordination Test**
```
1. /debugp2deploy resource:hand_crews count:2 → Player 2 deploys 2 Ground Crews
2. Use buttons to deploy Engine Company as Player 1
3. /debugstatus → See all team resources deployed
4. Watch how team resources affect fire suppression
```

### **Budget Depletion Test**
```
1. Keep deploying expensive resources (Air Support $5k each)
2. Test what happens when team budget runs out
3. Verify budget coordination prevents overspending
```

## 🚀 **WHAT YOU'LL SEE**

### **Team Notifications (Every 45 seconds):**
```
📈 **TEAM FIRE UPDATE - GUILD FIRE XXXX**

EXCELLENT TEAM COORDINATION!

🔥 **CURRENT STATUS:**
• Size: 15 acres (-5.2 acres)
• Containment: 45% (+15.8%)
• Threat: 🟡 MODERATE - 3 structures at risk

👥 **TEAM RESOURCES:**
• Ground Crews: 2 units
• Engines: 1 unit
• Air Support: 2 units
• Dozers: 0 units

💰 Team Budget: $32k remaining
📊 Team earned +$8k budget! Great coordination!

Team members use /respond to deploy more resources!
```

### **Debug Status Output:**
```
🧪 **DEBUG STATUS - MULTIPLAYER FIRE**

📋 Fire ID: guild_fire_123456789_1234567890
📍 Channel ID: 123456789
⏰ Next Progression: 2025-06-19 10:30:45
📊 Status: active

👥 Team Responders:
• YourName (ID: 123456789)
• YourName-Player2 (ID: 124456788)

🚒 Resources Deployed:
• Ground Crews: 2 units
• Engines: 1 unit  
• Air Support: 2 units
• Dozers: 0 units

💰 Team Budget: $32k
🔥 Fire Size: 15 acres
📈 Containment: 45%

Auto-progression active every 45 seconds!
```

## 🎯 **SUCCESS INDICATORS**

You'll know multiplayer is working correctly when:
- ✅ **Team budget decreases** when either player deploys resources
- ✅ **Resource counts increase** for team deployments from both players
- ✅ **Auto-progression messages** appear every 45 seconds in guild channel
- ✅ **Team notifications show** both players' names in responders list
- ✅ **Mission success/failure** messages celebrate team coordination

## 🔧 **CLEANUP**

After testing, these debug commands can be easily removed by:
1. Deleting the debug command methods from the code
2. Re-syncing Discord commands

The debug commands are clearly marked with `🧪 [DEBUG]` prefix for easy identification.

---

**This gives you complete single-account multiplayer testing capability! 🎮🔥**