---
description: 搜尋並安裝 skills
---
Help discover and install skills from the open agent skills ecosystem.

## User Query

$ARGUMENTS

## Skills CLI Reference

The Skills CLI (`npx skills`) is the package manager for agent skills:

- `npx skills find [query]` - Search for skills
- `npx skills add <package>` - Install a skill
- `npx skills add <package> -g -y` - Install globally without prompts
- `npx skills check` - Check for updates
- `npx skills update` - Update all skills

**Browse skills at:** https://skills.sh/

## Workflow

### Step 1: Understand the Request

Identify from user query:
1. The domain (React, testing, deployment, etc.)
2. The specific task (writing tests, PR reviews, etc.)
3. Keywords to search

### Step 2: Search for Skills

Run search with relevant keywords:

!`npx skills find $ARGUMENTS 2>/dev/null || echo "Skills CLI not available. Install with: npm install -g skills"`

### Step 3: Present Results

If skills found:
1. Show skill name and description
2. Provide install command: `npx skills add <owner/repo@skill> -g -y`
3. Link to skills.sh for details

If no skills found:
1. Acknowledge no matches
2. Offer to help directly
3. Suggest creating custom skill: `npx skills init my-skill`

## Common Categories

| Category | Keywords |
|----------|----------|
| Web Dev | react, nextjs, typescript, tailwind |
| Testing | jest, playwright, e2e, testing |
| DevOps | deploy, docker, kubernetes, ci-cd |
| Docs | readme, changelog, api-docs |
| Quality | review, lint, refactor, best-practices |
| Design | ui, ux, design-system, accessibility |

## Example Searches

- "react performance" → React optimization skills
- "pr review" → Code review skills  
- "changelog" → Documentation skills
- "deploy" → Deployment/CI-CD skills
