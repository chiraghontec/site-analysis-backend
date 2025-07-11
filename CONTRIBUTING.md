# Contributing to Site Analysis Backend

Thank you for your interest in contributing to the Site Analysis Backend project! This document provides guidelines for contributing to this Django-based geospatial analysis platform.

## Development Workflow

### Branch Strategy

We use a Git Flow-inspired branching strategy:

- **`main`**: Production-ready code. Only merge from `develop` via pull requests.
- **`develop`**: Integration branch for features. All feature branches merge here first.
- **`feature/*`**: Feature development branches (e.g., `feature/climate-integration`)
- **`hotfix/*`**: Emergency fixes for production issues
- **`release/*`**: Release preparation branches

### Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/site-analysis-backend.git
   cd site-analysis-backend
   ```

2. **Set up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv site_env
   source site_env/bin/activate  # On Windows: site_env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up Database**
   Follow the instructions in `SETUP_POSTGRESQL.md` to set up PostgreSQL with PostGIS.

4. **Run Migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

### Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, well-documented code
   - Follow Django best practices
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run Django tests
   python manage.py test
   
   # Run API tests
   python test_api.py
   python test_climate_api.py
   
   # Check code style (install flake8 if needed)
   flake8 .
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add description of your feature"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `style:` for formatting changes

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a pull request from your feature branch to `develop`.

## Code Standards

### Python/Django
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Write docstrings for classes and functions
- Keep functions small and focused
- Use type hints where appropriate

### Geospatial Code
- Use GeoDjango's spatial features appropriately
- Validate coordinate reference systems (CRS)
- Handle spatial data efficiently
- Document spatial assumptions and limitations

### API Design
- Follow RESTful principles
- Use Django Ninja for API documentation
- Validate input data thoroughly
- Return consistent error responses
- Version your APIs appropriately

### Testing
- Write unit tests for models and services
- Write integration tests for API endpoints
- Test edge cases and error conditions
- Mock external API calls in tests
- Aim for good test coverage

## Database Migrations

- Always create migrations for model changes
- Review migrations before committing
- Test migrations on a copy of production data
- Never edit existing migrations
- Use descriptive migration names

## Environment Variables

- Never commit sensitive data (API keys, passwords)
- Update `.env.example` when adding new variables
- Document all environment variables in README
- Use secure defaults where possible

## Documentation

- Keep README.md up to date
- Document new features and APIs
- Include code examples
- Update setup instructions when needed
- Write clear commit messages

## Review Process

### Pull Request Requirements
- All tests must pass
- Code must be reviewed by at least one maintainer
- Feature branches merge to `develop`
- Only `develop` merges to `main`
- Include description of changes
- Reference any related issues

### Code Review Checklist
- [ ] Code follows project standards
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive data is committed
- [ ] Migrations are reviewed
- [ ] API changes are documented

## Release Process

1. Create release branch from `develop`
2. Update version numbers
3. Update CHANGELOG.md
4. Final testing
5. Merge to `main` and tag release
6. Deploy to production
7. Merge back to `develop`

## Getting Help

- Check existing issues and documentation
- Ask questions in pull request comments
- Contact maintainers for complex issues
- Follow the code of conduct

## Performance Considerations

- Optimize database queries (use `select_related`, `prefetch_related`)
- Cache expensive operations
- Use spatial indexes for geospatial queries
- Consider pagination for large datasets
- Monitor memory usage with large spatial datasets

## Security

- Validate all input data
- Use parameterized queries
- Follow OWASP guidelines
- Keep dependencies updated
- Review security implications of changes

Thank you for contributing to making site analysis more accessible and powerful!
