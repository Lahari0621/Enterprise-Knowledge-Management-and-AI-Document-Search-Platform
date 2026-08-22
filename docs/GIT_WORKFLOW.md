# Git Workflow
## Branching Strategy

This project uses separate branches for different areas of development:

- `master` - Default and integration branch containing the combined project.
- `frontend` - Used for frontend development and frontend-related changes.
- `backend` - Used for backend API and server-side development.
- `db` - Used for database-related development and database session management.

## Development Workflow
1. Development work is performed in the appropriate branch.
2. Changes are reviewed and committed with meaningful commit messages.
3. The development branch is pushed to the remote GitHub repository.
4. Completed changes are merged into the `master` branch.
5. The `master` branch represents the integrated version of the project.

## Commit Practices
Meaningful commit messages are used to describe the purpose of each change.
Examples from this project include:

- `Update frontend API configuration`
- `Improve backend API metadata`
- `Document database session management`
- `Merge backend into master`
- `Merge branch 'db'`

## Remote Repository
The project is maintained in a GitHub repository:

`Lahari0621/Enterprise-Knowledge-Management-and-AI-Document-Search-Platform`

## Benefits
This workflow keeps frontend, backend, and database development organized while allowing changes to be integrated into the default `master` branch.