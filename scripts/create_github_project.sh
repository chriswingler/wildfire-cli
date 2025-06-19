#!/bin/bash
# GitHub Project Creation Script
# Requires GitHub CLI with 'project' and 'read:project' scopes

set -e

echo "🚀 Creating GitHub Project for Wildfire CLI..."

# Step 1: Get repository owner ID
REPO_OWNER_ID=$(gh api graphql -f query='
{
  repository(owner: "chriswingler", name: "wildfire-cli") {
    owner {
      id
    }
  }
}' --jq '.data.repository.owner.id')

echo "📋 Repository Owner ID: $REPO_OWNER_ID"

# Step 2: Create the project
PROJECT_RESULT=$(gh api graphql -f query="
mutation {
  createProjectV2(input: {
    ownerId: \"$REPO_OWNER_ID\"
    title: \"Wildfire CLI Development\"
    description: \"Sprint planning and kanban workflow for wildfire-cli development\"
  }) {
    projectV2 {
      id
      number
      title
      url
    }
  }
}")

PROJECT_ID=$(echo "$PROJECT_RESULT" | jq -r '.data.createProjectV2.projectV2.id')
PROJECT_NUMBER=$(echo "$PROJECT_RESULT" | jq -r '.data.createProjectV2.projectV2.number')
PROJECT_URL=$(echo "$PROJECT_RESULT" | jq -r '.data.createProjectV2.projectV2.url')

echo "✅ Project Created!"
echo "   Project ID: $PROJECT_ID"
echo "   Project Number: $PROJECT_NUMBER"
echo "   Project URL: $PROJECT_URL"

# Step 3: Add repository to project
gh api graphql -f query="
mutation {
  linkRepositoryToProjectV2(input: {
    projectId: \"$PROJECT_ID\"
    repositoryId: \"$(gh api repos/chriswingler/wildfire-cli --jq '.node_id')\"
  }) {
    repository {
      id
    }
  }
}"

echo "🔗 Repository linked to project"

# Step 4: Get project fields for configuration
FIELDS_RESULT=$(gh api graphql -f query="
{
  node(id: \"$PROJECT_ID\") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}")

echo "📊 Project fields retrieved"

# Step 5: Add custom fields
echo "🔧 Creating custom fields..."

# Story Points field
STORY_POINTS_FIELD=$(gh api graphql -f query="
mutation {
  createProjectV2Field(input: {
    projectId: \"$PROJECT_ID\"
    dataType: NUMBER
    name: \"Story Points\"
  }) {
    projectV2Field {
      id
      name
    }
  }
}")

# Sprint field
SPRINT_FIELD=$(gh api graphql -f query="
mutation {
  createProjectV2Field(input: {
    projectId: \"$PROJECT_ID\"
    dataType: SINGLE_SELECT
    name: \"Sprint\"
    singleSelectOptions: [
      {name: \"Sprint 4\", color: \"GREEN\"},
      {name: \"Sprint 5\", color: \"BLUE\"},
      {name: \"Future\", color: \"GRAY\"}
    ]
  }) {
    projectV2Field {
      id
      name
    }
  }
}")

echo "✅ Custom fields created"

# Step 6: Add existing issues to project
echo "📝 Adding existing issues to project..."

# Get all issues
ISSUES=$(gh issue list --json number,title,labels,milestone --limit 100)

# Add each issue to project
echo "$ISSUES" | jq -r '.[] | @base64' | while read issue; do
    ISSUE_DATA=$(echo "$issue" | base64 -d)
    ISSUE_NUMBER=$(echo "$ISSUE_DATA" | jq -r '.number')
    ISSUE_TITLE=$(echo "$ISSUE_DATA" | jq -r '.title')
    
    echo "  Adding Issue #$ISSUE_NUMBER: $ISSUE_TITLE"
    
    # Get issue node ID
    ISSUE_NODE_ID=$(gh api repos/chriswingler/wildfire-cli/issues/$ISSUE_NUMBER --jq '.node_id')
    
    # Add issue to project
    gh api graphql -f query="
    mutation {
      addProjectV2ItemByContentId(input: {
        projectId: \"$PROJECT_ID\"
        contentId: \"$ISSUE_NODE_ID\"
      }) {
        item {
          id
        }
      }
    }" > /dev/null
done

echo "✅ All issues added to project"

# Step 7: Create project views
echo "🔍 Creating project views..."

# Kanban Workflow View
gh api graphql -f query="
mutation {
  createProjectV2View(input: {
    projectId: \"$PROJECT_ID\"
    name: \"Kanban Workflow\"
    layout: BOARD_LAYOUT
  }) {
    projectV2View {
      id
      name
    }
  }
}" > /dev/null

# Sprint Planning View  
gh api graphql -f query="
mutation {
  createProjectV2View(input: {
    projectId: \"$PROJECT_ID\"
    name: \"Sprint Planning\"
    layout: BOARD_LAYOUT
  }) {
    projectV2View {
      id
      name
    }
  }
}" > /dev/null

# Work Stream View
gh api graphql -f query="
mutation {
  createProjectV2View(input: {
    projectId: \"$PROJECT_ID\"
    name: \"Work Streams\"
    layout: BOARD_LAYOUT
  }) {
    projectV2View {
      id
      name
    }
  }
}" > /dev/null

echo "✅ Project views created"

echo ""
echo "🎉 GitHub Project setup complete!"
echo "   Access your project at: $PROJECT_URL"
echo ""
echo "📋 Next Steps:"
echo "   1. Configure view groupings in GitHub UI"
echo "   2. Set up project automation rules"
echo "   3. Add story point values to Sprint 4 issues"
echo ""
echo "🔗 Sprint 4 Issues Ready:"
echo "   • Issue #22: Discord Interactive Interface (6 pts)"
echo "   • Issue #23: Rookie Commander Tutorial (6 pts)"
echo "   • Issue #24: Real-time Game Feel (6 pts)"