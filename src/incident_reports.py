"""
@file incident_reports.py
@brief Generate authentic wildfire incident reports from simulation data
@details Converts fire grid state to professional ICS-style reports
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List
from fire_engine import FireGrid, TerrainType


class IncidentReportGenerator:
    """
    @brief Generate professional wildfire incident reports
    @details Converts internal simulation to authentic ICS terminology and format
    """
    
    def __init__(self):
        self.incident_names = [
            "Wildcat Fire", "Ridge Runner Fire", "Smokey Hills Fire", 
            "Grassland Fire", "Valley View Fire", "Pine Creek Fire",
            "Sunset Mesa Fire", "Canyon Wind Fire", "Cedar Grove Fire"
        ]
        self.location_descriptors = [
            "steep terrain with limited access roads",
            "mixed fuel types including grass and timber",
            "interface area with residential structures",
            "remote wilderness with helicopter access only", 
            "agricultural area with seasonal crop residue",
            "heavy timber with significant fire loading"
        ]
        
    def generate_incident_name(self) -> str:
        """Generate realistic fire incident name."""
        return random.choice(self.incident_names)
    
    def generate_initial_dispatch_report(self, fire_grid: FireGrid, incident_name: str) -> str:
        """Generate initial dispatch report for fire discovery."""
        stats = fire_grid.get_fire_statistics()
        threats = fire_grid.get_threat_assessment()
        location_desc = random.choice(self.location_descriptors)
        
        report = f"""🚨 **INITIAL DISPATCH REPORT - {incident_name.upper()}**

**INCIDENT INFORMATION**
• **Incident Name:** {incident_name}
• **Incident Number:** {datetime.now().strftime('%Y')}-{random.randint(1000, 9999)}
• **Report Time:** {datetime.now().strftime('%H%M hours, %d %b %Y')}
• **Incident Commander:** IC-{random.randint(100, 999)}

**FIRE SITUATION**
• **Current Size:** {stats['fire_size_acres']} acres
• **Rate of Spread:** {'Rapid' if stats['active_cells'] > 3 else 'Moderate' if stats['active_cells'] > 1 else 'Slow'}
• **Fire Behavior:** {'Extreme' if stats['weather']['fire_danger'] == 'EXTREME' else 'Active' if stats['weather']['fire_danger'] in ['HIGH', 'MODERATE'] else 'Minimal'}
• **Containment:** {stats['containment_percent']}%

**WEATHER CONDITIONS**
• **Wind:** {stats['weather']['wind_direction']} at {stats['weather']['wind_speed']} mph
• **Temperature:** {stats['weather']['temperature']}°F
• **Relative Humidity:** {stats['weather']['humidity']}%
• **Fire Weather Rating:** {stats['weather']['fire_danger']}

**THREAT ASSESSMENT**
• **Structures Threatened:** {threats['threatened_structures']}
• **Threat Level:** {threats['threat_level']}
• **Evacuation Status:** {'RECOMMENDED' if threats['evacuation_recommended'] else 'NONE REQUIRED'}

**LOCATION & ACCESS**
• **General Location:** Fire occurring in {location_desc}
• **Primary Access:** Via incident command post
• **Terrain Challenges:** Variable terrain affecting suppression tactics

**INITIAL TACTICAL OBJECTIVES**
1. **Life Safety:** Ensure firefighter and public safety
2. **Incident Stabilization:** Establish containment lines
3. **Property Conservation:** Protect threatened structures

**RESOURCES REQUESTED**
• Additional ground resources for initial attack
• Air support if weather permits
• Structure protection as needed

**NEXT UPDATE:** Operational briefing in 2 hours or significant change

---
*Incident Command System • Educational Wildfire Simulation*"""

        return report
    
    def generate_operational_briefing(self, fire_grid: FireGrid, incident_name: str) -> str:
        """Generate operational period briefing."""
        stats = fire_grid.get_fire_statistics()
        threats = fire_grid.get_threat_assessment()
        
        # Determine fire behavior trend
        if stats['active_cells'] > 5:
            behavior_trend = "INCREASING"
            behavior_desc = "Fire activity remains high with potential for continued growth"
        elif stats['active_cells'] > 2:
            behavior_trend = "MODERATE"
            behavior_desc = "Fire showing moderate activity with opportunities for containment"
        else:
            behavior_trend = "DECREASING"
            behavior_desc = "Fire activity decreasing, good progress on containment"
        
        report = f"""📋 **OPERATIONAL BRIEFING - {incident_name.upper()}**

**OPERATIONAL PERIOD {stats['operational_period']} BRIEFING**
• **Time:** {datetime.now().strftime('%H%M hours, %d %b %Y')}
• **Incident Duration:** {stats['incident_duration']}
• **Briefing Officer:** Plans Section Chief

**CURRENT SITUATION**
• **Fire Size:** {stats['fire_size_acres']} acres
• **Containment:** {stats['containment_percent']}%
• **Fire Behavior:** {behavior_trend} - {behavior_desc}
• **Active Perimeter:** {stats['active_cells']} active sectors

**WEATHER FORECAST**
• **Current Conditions:** {stats['weather']['wind_direction']} winds {stats['weather']['wind_speed']} mph
• **Temperature:** {stats['weather']['temperature']}°F, RH {stats['weather']['humidity']}%
• **Fire Weather:** {stats['weather']['fire_danger']} danger rating
• **Forecast Reliability:** {'High confidence' if random.random() > 0.3 else 'Moderate confidence'}

**CRITICAL INFORMATION**
• **Structure Threat:** {threats['threatened_structures']} structures at risk
• **Threat Level:** {threats['threat_level']}
• **Public Safety:** {'Evacuation in effect' if threats['evacuation_recommended'] else 'No evacuations required'}

**TACTICAL PRIORITIES**
1. **Primary:** {'Structure protection and public safety' if threats['threat_level'] in ['HIGH', 'EXTREME'] else 'Establish containment lines'}
2. **Secondary:** {'Containment on flanks' if stats['containment_percent'] < 50 else 'Mop-up and patrol'}
3. **Tertiary:** {'Prepare for extended operations' if stats['fire_size_acres'] > 100 else 'Resource demobilization planning'}

**SUPPRESSION STRATEGY**
• **Direct Attack:** {'Not recommended' if stats['weather']['fire_danger'] == 'EXTREME' else 'Opportunities available'}
• **Indirect Attack:** {'Primary strategy' if stats['fire_size_acres'] > 50 else 'Secondary option'}
• **Tactical Approach:** {'Defensive' if threats['threat_level'] in ['HIGH', 'EXTREME'] else 'Offensive'}

**SAFETY CONSIDERATIONS**
• **Weather Impact:** Wind conditions affecting suppression operations
• **Terrain Hazards:** Variable terrain requiring tactical adjustments
• **Communication:** Maintain radio contact with command post
• **Escape Routes:** Ensure safety zones and escape routes identified

**NEXT OPERATIONAL PERIOD**
• **Duration:** 12 hours
• **Objectives:** {'Focus on structure protection' if threats['threat_level'] in ['HIGH', 'EXTREME'] else 'Continue containment efforts'}
• **Resource Needs:** Additional assessment pending

---
*End of Briefing - Questions to Plans Section*"""

        return report
    
    def generate_resource_status_report(self, resources_deployed: Dict) -> str:
        """Generate resource status and effectiveness report."""
        total_personnel = sum(resources_deployed.values())
        
        report = f"""👥 **RESOURCE STATUS REPORT**

**CURRENT DEPLOYMENT**
• **Total Personnel:** {total_personnel} firefighters assigned
• **Ground Resources:** {resources_deployed.get('hand_crews', 0)} hand crews
• **Engines:** {resources_deployed.get('engines', 0)} engine companies
• **Air Resources:** {resources_deployed.get('air_tankers', 0)} aircraft available

**RESOURCE EFFECTIVENESS**
• **Suppression Progress:** {'Excellent' if total_personnel > 60 else 'Good' if total_personnel > 30 else 'Limited'} progress with current resources
• **Resource Utilization:** {'Optimal' if total_personnel > 40 else 'Adequate' if total_personnel > 20 else 'Insufficient'}
• **Tactical Success:** Based on deployment and fire conditions

**RESOURCE REQUESTS**
• **Additional Needs:** {'No additional resources required' if total_personnel > 50 else 'Additional ground resources recommended'}
• **Air Support:** {'Effective when weather permits' if resources_deployed.get('air_tankers', 0) > 0 else 'Request air resources'}

**OPERATIONAL NOTES**
• All resources operating within established safety protocols
• Resource assignments updated based on tactical priorities
• Demobilization planning initiated for contained sectors

---
*Resource Unit • Incident Command Post*"""

        return report
    
    def generate_situation_update(self, fire_grid: FireGrid, incident_name: str, 
                                special_note: str = None) -> str:
        """Generate situation update report for significant changes."""
        stats = fire_grid.get_fire_statistics()
        threats = fire_grid.get_threat_assessment()
        
        # Determine update priority
        if threats['threat_level'] in ['HIGH', 'EXTREME']:
            priority = "URGENT"
        elif stats['containment_percent'] > 75:
            priority = "ROUTINE"
        else:
            priority = "NORMAL"
        
        report = f"""📢 **SITUATION UPDATE - {priority}**

**{incident_name.upper()} - {datetime.now().strftime('%H%M HRS')}**

**FIRE STATUS CHANGE**
• **Size:** {stats['fire_size_acres']} acres ({'+' if random.random() > 0.3 else '='}{random.randint(0, 20)} acres since last report)
• **Containment:** {stats['containment_percent']}% contained
• **Active Burning:** {stats['active_cells']} active sectors

**SIGNIFICANT DEVELOPMENTS**"""

        if special_note:
            report += f"\n• {special_note}"
        
        if threats['evacuation_recommended']:
            report += "\n• **EVACUATION ADVISORY:** Residents advised to prepare for evacuation"
        
        if stats['weather']['fire_danger'] == 'EXTREME':
            report += "\n• **WEATHER ALERT:** Extreme fire weather conditions"
        
        if stats['containment_percent'] > 50:
            report += "\n• **CONTAINMENT PROGRESS:** Significant progress on fire perimeter"
        
        report += f"""

**IMMEDIATE ACTIONS**
• Continue {'structure protection' if threats['threat_level'] in ['HIGH', 'EXTREME'] else 'suppression operations'}
• {'Prepare for possible evacuation' if threats['evacuation_recommended'] else 'Monitor fire progression'}
• Maintain communication with incident command

**NEXT UPDATE:** {'In 1 hour' if priority == 'URGENT' else 'Next operational period'} or significant change

---
*Information Officer • {datetime.now().strftime('%H%M hrs')}*"""

        return report
    
    def generate_after_action_report(self, fire_grid: FireGrid, incident_name: str,
                                   final_stats: Dict) -> str:
        """Generate after-action report for completed incident."""
        lessons = [
            "Early detection and rapid initial attack proved effective",
            "Coordination between ground and air resources was essential",
            "Weather monitoring provided critical tactical advantage",
            "Structure protection priorities were properly established",
            "Resource deployment timing impacted suppression success",
            "Communication systems performed well under operational stress"
        ]
        
        selected_lessons = random.sample(lessons, 3)
        
        report = f"""📊 **AFTER ACTION REPORT - {incident_name.upper()}**

**INCIDENT SUMMARY**
• **Final Size:** {final_stats['fire_size_acres']} acres
• **Containment:** {final_stats['containment_percent']}% at control
• **Duration:** {final_stats['incident_duration']}
• **Operational Periods:** {final_stats['operational_period']}

**INCIDENT OUTCOMES**
• **Structures:** {final_stats['threatened_structures']} structures threatened, {'significant protection achieved' if final_stats['containment_percent'] > 70 else 'mixed protection results'}
• **Suppression Success:** {'Highly effective' if final_stats['containment_percent'] > 80 else 'Effective' if final_stats['containment_percent'] > 50 else 'Challenging conditions'}
• **Resource Efficiency:** Multiple resources deployed effectively

**LESSONS LEARNED**
1. {selected_lessons[0]}
2. {selected_lessons[1]}
3. {selected_lessons[2]}

**TACTICAL PERFORMANCE**
• **Decision Making:** {'Excellent' if final_stats['containment_percent'] > 75 else 'Good' if final_stats['containment_percent'] > 50 else 'Room for improvement'} tactical decisions under pressure
• **Resource Management:** Effective allocation of available resources
• **Safety Record:** All operations conducted within safety protocols

**EDUCATIONAL OBJECTIVES MET**
✅ Understanding of Incident Command System structure
✅ Application of wildfire suppression tactics
✅ Experience with operational period planning
✅ Practice with resource allocation decisions

**RECOMMENDATIONS FOR FUTURE INCIDENTS**
• Continue emphasis on early detection and rapid response
• Maintain strong communication between all operational units
• Regular weather monitoring and tactical adjustments

---
*This concludes the {incident_name} simulation*
*Incident Command System Educational Experience*"""

        return report