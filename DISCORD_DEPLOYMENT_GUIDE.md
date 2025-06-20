# 🔥 Discord Wildfire MMORPG - Standalone Bot Deployment

## ⚡ Quick Start - Choose Your Deployment

### 🔥 Option 1: DigitalOcean App Platform (Recommended - 2 Minutes)

**One-Command Cloud Deployment:**
```bash
# Deploy directly from GitHub to DigitalOcean cloud
./deploy.sh
```

**What it does:**
- ✅ Deploys from your GitHub repo automatically
- ✅ Sets up 24/7 hosting on DigitalOcean ($5/month)
- ✅ Handles scaling and updates automatically
- ✅ Professional production environment

### 🖥️ Option 2: Local Development (5 Minutes)

**Run locally for testing:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure bot token
cp .env.example .env
# Edit .env with your Discord bot token

# 3. Run locally
python src/main.py
```

## 🔧 DigitalOcean Setup Details

### Prerequisites
1. **GitHub Account**: Your code repository
2. **DigitalOcean Account**: Sign up at digitalocean.com
3. **Discord Bot**: Create at discord.com/developers/applications

### Deployment Steps
```bash
# 1. Clone your repo (if not already)
git clone https://github.com/yourusername/wildfire-cli
cd wildfire-cli

# 2. Run deployment script
./deploy.sh

# 3. Add Discord token in DigitalOcean dashboard
# Go to: https://cloud.digitalocean.com/apps
# Add DISCORD_TOKEN in Environment Variables
```

### Environment Variables

Your Wildfire Discord Bot requires certain environment variables to be set in the DigitalOcean App Platform interface to function correctly. These variables contain sensitive information or configuration specific to your deployment.

*   **`DISCORD_TOKEN`**:
    *   **Purpose**: This is the authentication token for your Discord bot. It allows the application to connect to Discord and interact with servers as your bot.
    *   **How to Obtain**: You can get this token from your bot's application page on the [Discord Developer Portal](https://discord.com/developers/applications).
    *   **Setup**: During deployment via `deploy.sh`, or manually afterwards, you need to set this variable in your DigitalOcean App's "Settings" tab, under the "App-Level Environment Variables" section. **Store this token securely. Do not share it or commit it to the repository.**

*   **(Future Variables)**:
    *   If other services or configurations are added that require API keys or specific settings (e.g., a database connection string if persistence is added), they will be listed here.

### After Deployment
- **Bot URL**: Visible in DigitalOcean Apps dashboard
- **Logs**: `doctl apps logs YOUR_APP_ID --type run`
- **Cost**: ~$5/month for basic tier
- **Scaling**: Automatic based on usage

## 🎮 Test Commands
In your Discord server:
- `/fire` - Creates a new wildfire incident
- `/respond` - Join the fire response team  
- `/firestatus` - Check status of all active fires

## 🎮 How It Works

### Basic Gameplay Loop
1. **Someone uses `/fire`** → New wildfire incident created
2. **Players use `/respond`** → Join the firefighting team
3. **Use `/firestatus`** → See fire containment progress
4. **More responders = faster containment**

### Simple Mechanics
- **Fire Properties**: Type (grass/forest/interface), size, threat level
- **Player Roles**: Everyone starts as "firefighter"
- **Containment**: Increases based on number of responders (15% per responder)
- **Status Updates**: Real-time progress tracking

## 🔧 Technical Details

### Following Coding Standards
- ✅ Functions under 60 lines
- ✅ Single responsibility principle  
- ✅ Descriptive naming conventions
- ✅ Simple error handling
- ✅ KISS principle implementation
- ✅ YAGNI - only essential dependencies

### Data Storage
- **SQLite Database**: Persistent game state across bot restarts
- **Async Operations**: Non-blocking database operations
- **Multi-Server**: Independent game states per Discord server
- **Scalable**: Ready for UEMini backend integration

### Discord Integration
- **Slash Commands**: Modern Discord command interface
- **Rich Embeds**: Professional information display with color coding
- **Rate Limiting**: Built-in cooldown management
- **Error Handling**: Robust exception handling and logging

## 🛠️ Disaster Recovery / Redeployment

If the bot's DigitalOcean deployment becomes corrupted, is accidentally deleted, or requires a full redeployment for any other reason, follow these steps to restore service:

1.  **Verify Source Code:**
    *   Ensure the `main` branch of your GitHub repository (`chriswingler/wildfire-cli` or your fork) contains the latest stable and correct version of the bot's code.

2.  **Deploy or Redeploy on DigitalOcean:**
    *   **If the app was deleted:** Run the `./deploy.sh` script from your local repository. This will provision a new app instance on DigitalOcean using the settings in your `.do/app.yaml` file.
    *   **If the app still exists:** You can trigger a manual redeploy from the DigitalOcean dashboard. Navigate to your app, go to the "Actions" menu, and select "Deploy" or "Force Rebuild and Deploy." Ensure it's configured to pull from the correct GitHub repository and branch (`main`).

3.  **Configure Environment Variables:**
    *   After deployment, go to your app's page in the DigitalOcean dashboard.
    *   Navigate to the "Settings" tab.
    *   Under "App-Level Environment Variables," ensure that all required variables are present and correctly set. Refer to the "Environment Variables" section of this guide for details.
    *   You will need to manually enter the value for `DISCORD_TOKEN` (and any other secrets) from your secure storage (e.g., password manager). **These secret values are not stored in the repository.**

4.  **Test the Bot:**
    *   Once the deployment is complete and environment variables are set, test the bot in your Discord server(s) to ensure it is online and functioning as expected.

**Important Considerations:**

*   **Data Persistence:** As of the current design, the bot stores game state (active fires, user progress) in memory. This means that upon redeployment, any ongoing games or user states will be lost. Implementing persistent data storage (e.g., using a database) is required to recover game data across redeployments. This is planned as a future enhancement.
*   **GitHub Access:** Ensure DigitalOcean has the necessary permissions to access your GitHub repository for deployment. This is usually configured when first setting up the app.

## 🛡️ Backup and Recovery Maintenance Schedule

To ensure the continued integrity of your bot's backup and recovery mechanisms, it's recommended to perform the following checks and tests periodically:

**1. Configuration (Environment Variables & `DISCORD_TOKEN`):**

*   **Token Accessibility & Correctness Check (Annually, or as needed):**
    *   Verify that your securely stored `DISCORD_TOKEN` value is up-to-date and accessible to you (e.g., in your password manager).
    *   If you regenerate your token from Discord, ensure your stored value is immediately updated.
*   **Documentation Review (Every 6 Months, or on process change):**
    *   Review the "Environment Variables" and "Disaster Recovery / Redeployment" sections in this guide (`DISCORD_DEPLOYMENT_GUIDE.md`).
    *   Ensure the documented procedures and required variables still accurately reflect your deployment setup. Update as necessary.
*   **Full Recovery Test (Annually):**
    *   Perform a full recovery test by following the "Disaster Recovery / Redeployment" steps. This includes redeploying the application and re-configuring the environment variables as if recovering from a failure. This ensures the process is familiar and all components (scripts, DigitalOcean settings, token access) work as expected.

**2. Source Code (GitHub):**

*   **Ongoing:** Your regular development and deployment process (pushing to GitHub, deploying to DigitalOcean) implicitly tests the integrity of the source code backup and its deployability. Ensure the `main` branch always represents the intended production code.

**3. Persistent Data (Future):**

*   **(Currently N/A as game state is in-memory)**
*   If persistent data storage (e.g., SQLite database) is implemented in the future:
    *   **Daily/Weekly:** Verify automated backup jobs for the database are running successfully.
    *   **Quarterly/Bi-Annually:** Perform a test restoration of the database from a backup to a staging/test environment to ensure data integrity and familiarize yourself with the restoration process.

Adhering to this schedule will help catch any issues with your backup and recovery strategy before they become critical.

## 🚀 Next Steps

### Immediate Enhancements (Today)
1. **Persistence**: Add SQLite database for fire state
2. **Timers**: Automatic fire progression over time
3. **Roles**: Different firefighter specializations
4. **Channels**: Separate channels for different incidents

### Medium Term (This Week)
1. **Advanced Simulation**: Integrate with fire spread algorithm
2. **Weather System**: Dynamic conditions affecting fires
3. **Resource Management**: Equipment and cost tracking
4. **Player Progression**: XP and advancement system

### Long Term (This Month)
1. **UEMini Integration**: Professional game engine backend
2. **Multi-Server**: Independent game states per Discord server
3. **MMORPG Features**: Guilds, rankings, competitions
4. **Cross-Platform**: Link to main Unreal game development

## 🎯 Success Metrics

### Today's Goals
- [ ] `/fire` command working in Discord
- [ ] Players can `/respond` to incidents  
- [ ] `/firestatus` shows progress
- [ ] Multiple concurrent fires supported
- [ ] Community engagement and testing

### This Week's Goals
- [ ] 10+ community members tested the game
- [ ] Fire incidents persist across sessions
- [ ] Basic progression system implemented
- [ ] Integration with existing BlazeBot features

## 🔥 Ready to Deploy!

This implementation follows **KISS principles** from your coding standards:
- **Minimal complexity** for immediate deployment
- **Single responsibility** functions
- **Clear, descriptive** naming
- **Simple state management**
- **Easy to extend** architecture

**Time to deploy**: ~5 minutes for standalone bot
**Time to test**: ~30 seconds in Discord  
**Community ready**: Immediately!

## 🚀 Architecture Benefits

This repurposed architecture provides:
- **Proven Infrastructure**: BlazeBot's robust Discord framework
- **Clean Codebase**: Simplified, focused on wildfire game only
- **Professional Features**: Rate limiting, error handling, logging
- **Scalable Foundation**: Ready for MMORPG feature expansion

Go make some fires! 🚒