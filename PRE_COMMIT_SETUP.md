# Pre-commit Setup for DerivWorkFLow

This document explains the pre-commit configuration for the DerivWorkFLow project, which ensures code quality and consistency across both frontend and backend codebases.

## 🚀 Quick Setup

Run the automated setup script:

```bash
./scripts/setup-pre-commit.sh
```

This script will:
- Install all necessary dependencies
- Set up pre-commit hooks
- Create initial baselines
- Configure all tools

## 📋 What's Included

### Backend (Python) Tools
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security analysis

### Frontend (TypeScript/React) Tools
- **ESLint**: Code linting with TypeScript and React rules
- **Prettier**: Code formatting
- **TypeScript**: Type checking

### General Tools
- **pre-commit-hooks**: Basic file checks
- **detect-secrets**: Secret detection
- **hadolint**: Dockerfile linting

## 🛠️ Manual Setup

If you prefer to set up manually:

### 1. Install Dependencies

**Frontend:**
```bash
cd apps/frontend
npm install
```

**Backend:**
```bash
cd apps/backend
pipenv install --dev
```

### 2. Install Pre-commit
```bash
pip install pre-commit
```

### 3. Install Hooks
```bash
pre-commit install
```

### 4. Create Secrets Baseline
```bash
detect-secrets scan --baseline .secrets.baseline
```

## 📝 Available Commands

### Root Level (from project root)
```bash
# Pre-commit commands
npm run pre-commit:run          # Run on all files
npm run pre-commit:run-changed  # Run on changed files

# Combined commands
npm run format:all              # Format all code
npm run lint:all                # Lint all code
npm run type-check:all          # Type check all code
```

### Frontend (from apps/frontend)
```bash
npm run lint                    # Lint TypeScript/React code
npm run lint:fix                # Lint and auto-fix
npm run format                  # Format code with Prettier
npm run format:check            # Check formatting
npm run type-check              # TypeScript type checking
```

### Backend (from apps/backend)
```bash
pipenv run format               # Format with Black and isort
pipenv run format-check         # Check formatting
pipenv run lint                 # Lint with flake8 and bandit
pipenv run type-check           # Type check with mypy
```

## 🔧 Configuration Files

- `.pre-commit-config.yaml` - Main pre-commit configuration
- `apps/backend/pyproject.toml` - Python tool configurations
- `apps/frontend/.eslintrc.json` - ESLint configuration
- `apps/frontend/.prettierrc` - Prettier configuration

## 🎯 How It Works

1. **On Commit**: Pre-commit hooks run automatically before each commit
2. **File Filtering**: Tools only run on relevant files (Python tools on backend, JS/TS tools on frontend)
3. **Auto-fix**: Some tools automatically fix issues (Black, isort, Prettier)
4. **Blocking**: Commits are blocked if issues cannot be auto-fixed

## 🔍 Troubleshooting

### Common Issues

**Pre-commit fails on first run:**
```bash
pre-commit run --all-files
```

**Update pre-commit hooks:**
```bash
pre-commit autoupdate
```

**Skip pre-commit (emergency only):**
```bash
git commit --no-verify -m "Emergency commit"
```

**Reinstall hooks:**
```bash
pre-commit uninstall
pre-commit install
```

### Tool-Specific Issues

**Black formatting conflicts:**
```bash
cd apps/backend
pipenv run black .
```

**ESLint issues:**
```bash
cd apps/frontend
npm run lint:fix
```

**TypeScript errors:**
```bash
cd apps/frontend
npm run type-check
```

## 📊 Code Quality Standards

### Python (Backend)
- Line length: 88 characters (Black default)
- Import sorting: isort with Black profile
- Type hints: Required for all functions
- Security: Bandit checks for common vulnerabilities

### TypeScript/React (Frontend)
- Line length: 80 characters
- Quotes: Single quotes preferred
- Semicolons: Required
- Accessibility: ESLint jsx-a11y rules enforced

## 🔐 Security

The setup includes:
- **detect-secrets**: Scans for hardcoded secrets
- **bandit**: Python security analysis
- **ESLint security rules**: Frontend security checks

## 📈 Continuous Integration

Pre-commit hooks can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

## 🤝 Contributing

When contributing to the project:

1. Ensure pre-commit hooks are installed
2. Run `npm run format:all` before committing
3. Fix any linting issues
4. Ensure all type checks pass

## 📚 Additional Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [ESLint Documentation](https://eslint.org/)
- [Prettier Documentation](https://prettier.io/)
