# Multiplayer Testing Guide

## Quick Test Scenarios

### 2-User Team Test
1. **Setup**: Two users in Discord guild channel
2. **User A**: `/fire` → Creates team incident
3. **User B**: `/respond` → Joins team
4. **Both**: Deploy resources using interactive buttons
5. **System**: Auto-progression every 45 seconds
6. **Goal**: Coordinate to reach 100% containment

### Resource Coordination Test
1. **User A**: Deploy Ground Crews ($2k)
2. **User B**: Check `/firestatus` → See team resources
3. **User A**: Deploy Air Support ($5k) 
4. **System**: Team budget deducted, both see updates
5. **Goal**: Verify shared budget and visibility

### Auto-Progression Test
1. **Create fire**: `/fire` in guild channel
2. **Wait**: 45 seconds for auto-progression
3. **Observe**: Team update message in channel
4. **Goal**: Verify real-time progression works

## Expected Results
- ✅ Guild fires auto-progress every 45 seconds
- ✅ Team notifications sent to guild channel
- ✅ Shared team budget coordination
- ✅ Resource deployment visibility
- ✅ Mission success/failure for teams