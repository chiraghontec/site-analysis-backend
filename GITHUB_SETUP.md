# GitHub Setup and Workflow Guide

This guide will help you push your Site Analysis Backend project to GitHub and establish a professional development workflow.

## Initial GitHub Setup

### 1. Create GitHub Repository

1. **Go to GitHub.com** and sign in to your account
2. **Click "New repository"** or go to https://github.com/new
3. **Repository settings:**
   - Repository name: `site-analysis-backend`
   - Description: `Django backend for environmental site analysis with GeoDjango, PostGIS, and climate data integration`
   - Choose: Public or Private (your preference)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. **Click "Create repository"**

### 2. Connect Local Repository to GitHub

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/site-analysis-backend.git

# Verify remote was added
git remote -v

# Push main branch to GitHub
git push -u origin main

# Push develop branch to GitHub
git push -u origin develop
```

### 3. Set Up Branch Protection Rules

1. **Go to your repository on GitHub**
2. **Click Settings → Branches**
3. **Add rule for `main` branch:**
   - Branch name pattern: `main`
   - ✅ Require a pull request before merging
   - ✅ Require approvals: 1
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

4. **Add rule for `develop` branch:**
   - Branch name pattern: `develop`
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging

## Branching Strategy

### Branch Types

```
main (production)
├── develop (integration)
│   ├── feature/user-authentication
│   ├── feature/advanced-climate-analysis
│   ├── feature/data-visualization
│   └── feature/performance-optimization
├── hotfix/security-patch
└── release/v1.0.0
```

### Workflow Examples

#### Creating a New Feature

```bash
# Start from develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/user-authentication

# Work on your feature...
git add .
git commit -m "feat: add user authentication system"

# Push feature branch
git push -u origin feature/user-authentication

# Create Pull Request to develop via GitHub UI
```

#### Releasing to Production

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# Final testing and version updates...
git commit -m "chore: prepare release v1.0.0"
git push -u origin release/v1.0.0

# Create PR to main via GitHub UI
# After approval and merge:

# Tag the release
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Merge back to develop
git checkout develop
git merge main
git push origin develop
```

#### Emergency Hotfix

```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/security-vulnerability

# Fix the issue...
git commit -m "fix: patch security vulnerability"
git push -u origin hotfix/security-vulnerability

# Create PR to main via GitHub UI
# After merge, also merge to develop
```

## GitHub Secrets Setup

### Required Secrets for CI/CD

1. **Go to Settings → Secrets and variables → Actions**
2. **Add these secrets:**

   ```
   OPENWEATHER_API_KEY = your_openweather_api_key
   NASA_POWER_API_KEY = your_nasa_power_api_key
   DJANGO_SECRET_KEY = your_production_secret_key
   ```

### Optional Deployment Secrets

For automated deployment, add platform-specific secrets:

**Heroku:**
```
HEROKU_API_KEY = your_heroku_api_key
HEROKU_APP_NAME = your_heroku_app_name
```

**AWS:**
```
AWS_ACCESS_KEY_ID = your_aws_access_key
AWS_SECRET_ACCESS_KEY = your_aws_secret_key
```

**DigitalOcean:**
```
DIGITALOCEAN_ACCESS_TOKEN = your_do_token
```

## Issue and Project Management

### Issue Templates

Create `.github/ISSUE_TEMPLATE/` directory with templates:

1. **Bug Report** (bug_report.md)
2. **Feature Request** (feature_request.md)
3. **Documentation** (documentation.md)

### Project Board Setup

1. **Go to Projects tab** in your repository
2. **Create new project** → "Board"
3. **Add columns:**
   - 📋 Backlog
   - 🔄 In Progress
   - 👀 In Review
   - ✅ Done
   - 🚀 Released

### Labels

Create these labels for better organization:

```
bug (red) - Something isn't working
enhancement (blue) - New feature or request
documentation (green) - Improvements or additions to documentation
good first issue (purple) - Good for newcomers
help wanted (yellow) - Extra attention is needed
priority:high (red) - High priority
priority:medium (orange) - Medium priority
priority:low (gray) - Low priority
type:feature (blue) - New feature
type:refactor (gray) - Code refactoring
type:testing (green) - Related to testing
```

## Code Quality and Automation

### Pre-commit Hooks (Optional)

Set up pre-commit hooks for code quality:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

### Dependabot Configuration

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    target-branch: "develop"
    reviewers:
      - "your-username"
    commit-message:
      prefix: "deps"
      include: "scope"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Deployment Automation

### Heroku Deployment

Add to `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Heroku

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: ${{secrets.HEROKU_APP_NAME}}
        heroku_email: "your-email@example.com"
```

## Monitoring and Analytics

### GitHub Insights

Monitor your project health:

1. **Insights → Pulse** - Activity overview
2. **Insights → Contributors** - Contribution statistics
3. **Insights → Traffic** - Repository visits and clones
4. **Insights → Dependency graph** - Dependencies and vulnerabilities

### Issue Tracking

Use GitHub Issues effectively:

```bash
# Link commits to issues
git commit -m "fix: resolve database connection timeout (fixes #42)"

# Reference issues in PRs
git commit -m "feat: add climate data caching (addresses #38)"
```

## Team Collaboration

### Code Review Guidelines

1. **All changes go through Pull Requests**
2. **Require at least one approval**
3. **Run all tests before merging**
4. **Update documentation with changes**
5. **Keep PRs focused and small**

### Communication

1. **Use GitHub Discussions** for questions and ideas
2. **Create detailed issue descriptions**
3. **Reference related issues and PRs**
4. **Use clear commit messages**

## Security Best Practices

### Repository Security

1. **Enable vulnerability alerts**
2. **Use Dependabot for security updates**
3. **Never commit secrets or API keys**
4. **Regular security audits**
5. **Keep dependencies updated**

### Access Control

1. **Use teams for access management**
2. **Limit admin access**
3. **Regular access reviews**
4. **Two-factor authentication**

## Backup and Recovery

### Repository Backup

```bash
# Clone with all branches and history
git clone --mirror https://github.com/YOUR_USERNAME/site-analysis-backend.git

# Create periodic backups
git bundle create backup-$(date +%Y%m%d).bundle --all
```

### Data Backup

- Database backups (see DEPLOYMENT.md)
- Configuration backups
- Documentation versioning

## Next Steps

1. **Create GitHub repository**
2. **Push code to GitHub**
3. **Set up branch protection**
4. **Configure GitHub secrets**
5. **Create first issue/milestone**
6. **Set up project board**
7. **Invite collaborators**
8. **Configure deployment pipeline**

## Quick Command Reference

```bash
# Daily workflow
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
# ... make changes ...
git add .
git commit -m "feat: add my feature"
git push -u origin feature/my-feature
# Create PR via GitHub UI

# Keep develop updated
git checkout develop
git pull origin develop

# Update feature branch
git checkout feature/my-feature
git merge develop
git push origin feature/my-feature

# Delete merged feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

This setup provides a robust foundation for collaborative development and professional project management!
