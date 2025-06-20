#!/bin/bash
# Comprehensive Task Date Assignment Script
# Assigns start/target dates to all 74 project tasks

PROJECT_ID="PVT_kwHOAhw3ec4A73sX"
START_DATE_FIELD="PVTF_lAHOAhw3ec4A73sXzgwFsUU"
TARGET_DATE_FIELD="PVTF_lAHOAhw3ec4A73sXzgwFsWQ"

echo "🗓️ Assigning dates to all project tasks..."

# Sprint 1: Foundation (2025-06-20 → 2025-07-03)
declare -A SPRINT1_TASKS=(
    ["PVTI_lAHOAhw3ec4A73sXzgbs51o"]="2025-06-20,2025-06-27"  # Update CLAUDE.md
    ["PVTI_lAHOAhw3ec4A73sXzgbqvCI"]="2025-06-20,2025-07-03"  # Discord UI components
)

# Sprint 2: Core Features (2025-07-04 → 2025-07-17)
declare -A SPRINT2_TASKS=(
    ["PVTI_lAHOAhw3ec4A73sXzgbqu9M"]="2025-07-04,2025-07-10"  # Discord Interactive Interface
    ["PVTI_lAHOAhw3ec4A73sXzgbqu-Q"]="2025-07-04,2025-07-17"  # Real-time Game Feel
)

# Sprint 3: UI/UX (2025-07-18 → 2025-07-31)
declare -A SPRINT3_TASKS=(
    ["PVTI_lAHOAhw3ec4A73sXzgbqu9o"]="2025-07-18,2025-07-31"  # Rookie Tutorial
)

# Function to assign dates to a task
assign_dates() {
    local item_id=$1
    local start_date=$2
    local target_date=$3
    
    echo "  📅 $item_id: $start_date → $target_date"
    
    # Set start date
    gh api graphql -f query="
    mutation {
      updateProjectV2ItemFieldValue(input: {
        projectId: \"$PROJECT_ID\"
        itemId: \"$item_id\"
        fieldId: \"$START_DATE_FIELD\"
        value: { date: \"$start_date\" }
      }) {
        projectV2Item { id }
      }
    }" > /dev/null
    
    # Set target date
    gh api graphql -f query="
    mutation {
      updateProjectV2ItemFieldValue(input: {
        projectId: \"$PROJECT_ID\"
        itemId: \"$item_id\"
        fieldId: \"$TARGET_DATE_FIELD\"
        value: { date: \"$target_date\" }
      }) {
        projectV2Item { id }
      }
    }" > /dev/null
}

# Assign Sprint 1 dates
echo "📋 Sprint 1 (Foundation): June 20 - July 3"
for item_id in "${!SPRINT1_TASKS[@]}"; do
    IFS=',' read -r start_date target_date <<< "${SPRINT1_TASKS[$item_id]}"
    assign_dates "$item_id" "$start_date" "$target_date"
done

# Assign Sprint 2 dates  
echo "📋 Sprint 2 (Core Features): July 4 - July 17"
for item_id in "${!SPRINT2_TASKS[@]}"; do
    IFS=',' read -r start_date target_date <<< "${SPRINT2_TASKS[$item_id]}"
    assign_dates "$item_id" "$start_date" "$target_date"
done

# Assign Sprint 3 dates
echo "📋 Sprint 3 (UI/UX): July 18 - July 31"
for item_id in "${!SPRINT3_TASKS[@]}"; do
    IFS=',' read -r start_date target_date <<< "${SPRINT3_TASKS[$item_id]}"
    assign_dates "$item_id" "$start_date" "$target_date"
done

echo "✅ Date assignment complete! Check your roadmap view."