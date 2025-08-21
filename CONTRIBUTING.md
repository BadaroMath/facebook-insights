# Contributing to Facebook Analytics Platform

Thank you for your interest in contributing to the Facebook Analytics Platform! This document provides guidelines and information for contributors.

## 🎯 Getting Started

### Prerequisites
- Node.js 16+ and npm/yarn
- Python 3.9+
- MongoDB 4.4+
- Git knowledge
- Understanding of REST APIs and React

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/facebook-analytics-platform.git`
3. Create a virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -r requirements.txt && cd frontend && npm install`
5. Set up environment variables (see `.env.example` files)
6. Run tests to ensure everything works: `pytest && npm test`

## 🔄 Development Workflow

### Branch Naming Convention
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Maintain

Example:
```
feat(analytics): add real-time engagement metrics

- Implement WebSocket connection for live data
- Add engagement rate calculations
- Update dashboard components

Closes #123
```

## 🧪 Testing Guidelines

### Backend Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_analytics.py

# Run tests with verbose output
pytest -v
```

### Frontend Testing
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### Test Structure
- **Unit Tests**: Test individual functions/components
- **Integration Tests**: Test API endpoints and data flow
- **E2E Tests**: Test complete user workflows

## 🎨 Code Style Guidelines

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions/classes

```python
def calculate_engagement_rate(likes: int, comments: int, shares: int, reach: int) -> float:
    """
    Calculate engagement rate for a Facebook post.
    
    Args:
        likes: Number of likes
        comments: Number of comments
        shares: Number of shares
        reach: Post reach
        
    Returns:
        Engagement rate as a percentage
    """
    if reach == 0:
        return 0.0
    return ((likes + comments + shares) / reach) * 100
```

### JavaScript/React (Frontend)
- Use ESLint and Prettier configurations
- Use functional components with hooks
- Follow React best practices
- Use TypeScript for type safety

```jsx
interface EngagementMetricsProps {
  likes: number;
  comments: number;
  shares: number;
  reach: number;
}

const EngagementMetrics: React.FC<EngagementMetricsProps> = ({ 
  likes, 
  comments, 
  shares, 
  reach 
}) => {
  const engagementRate = useMemo(() => {
    if (reach === 0) return 0;
    return ((likes + comments + shares) / reach) * 100;
  }, [likes, comments, shares, reach]);

  return (
    <div className="engagement-metrics">
      <span>Engagement Rate: {engagementRate.toFixed(2)}%</span>
    </div>
  );
};
```

## 📝 Documentation

### Code Documentation
- All public functions must have docstrings/JSDoc
- Include parameter types and return values
- Provide usage examples for complex functions

### API Documentation
- Update OpenAPI/Swagger specs for new endpoints
- Include request/response examples
- Document error codes and messages

### README Updates
- Update feature lists for new functionality
- Add configuration instructions for new features
- Update setup instructions if needed

## 🐛 Bug Reports

### Before Submitting
1. Check existing issues to avoid duplicates
2. Try to reproduce the bug consistently
3. Test with the latest version

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g. iOS]
- Browser: [e.g. chrome, safari]
- Version: [e.g. 22]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Feature Request Template
```markdown
**Feature Description**
A clear description of the feature.

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How would you like this implemented?

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Screenshots, mockups, or examples.
```

## 🔍 Code Review Process

### For Contributors
1. Ensure all tests pass
2. Update documentation if needed
3. Keep PRs focused and atomic
4. Write clear PR descriptions

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact is minimal
- [ ] Backwards compatibility is maintained

## 🚀 Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes (backwards compatible)

### Release Steps
1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Tag release
5. Deploy to staging
6. Run full test suite
7. Deploy to production
8. Create GitHub release with notes

## 🤝 Community

### Communication Channels
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and discussions
- Discord: Real-time chat and community support

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the [Contributor Covenant](https://www.contributor-covenant.org/)

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Hall of Fame for long-term contributors

## 📚 Resources

### Learning Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api/)
- [MongoDB Documentation](https://docs.mongodb.com/)

### Development Tools
- [Postman Collection](./docs/postman-collection.json) for API testing
- [VSCode Settings](./.vscode/settings.json) for consistent development environment
- [Docker Compose](./docker-compose.dev.yml) for local development

Thank you for contributing to make Facebook Analytics Platform better! 🎉