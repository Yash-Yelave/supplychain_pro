# Branching System

This document outlines the branching strategy used for the Supply Chain Pro project on GitHub.

## Branches

### `main`
- **Purpose**: Production.
- **Usage**: The `main` branch is the production branch for both the backend and frontend. It should always contain stable, deployable code.

### `stagging`
- **Purpose**: Staging Area.
- **Usage**: The `stagging` branch is used as a review and staging area. All new features, updates, and bug fixes should be merged here first to be reviewed and tested before they are promoted to the production (`main`) branch.

## Workflow
1. Developers should create feature branches or push updates to the `stagging` branch.
2. Code on the `stagging` branch is reviewed and validated.
3. Once verified, the `stagging` branch is merged into the `main` branch for production deployment.
