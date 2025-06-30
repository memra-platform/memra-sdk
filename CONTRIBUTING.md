# Contributing to Memra SDK

Thank you for your interest in contributing to Memra! This guide will help you get started with development and ensure your contributions are smoothly integrated.

## 🚀 Quick Development Setup

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/memra-platform/memra-sdk.git
cd memra-sdk

# Create and activate conda environment
conda create -n memra-dev python=3.11
conda activate memra-dev

# Install development dependencies
pip install -e .
pip install -e ".[dev]"
```

### 2. Start Development Environment
```bash
# Set your API key
export MEMRA_API_KEY="your-api-key-here"

# Start services (PostgreSQL, MCP bridge)
docker-compose up -d
```

### 3. Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_execution.py

# Run with coverage
pytest --cov=memra
```

## 📁 Project Structure

```
memra-sdk/
├── memra/                    # Core framework
│   ├── __init__.py
│   ├── execution.py         # Execution engine
│   ├── models.py            # Data models
│   ├── tool_registry.py     # Tool management
│   └── discovery.py         # Service discovery
├── examples/                # Basic examples
├── demos/                   # Comprehensive demos
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── docker-compose.yml       # Development environment
```

## 🔧 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow the coding standards below
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes
```bash
# Run the test suite
pytest

# Run the demo to ensure it still works
python demos/etl_invoice_processing/etl_invoice_demo.py

# Test with a fresh database
docker-compose down -v
docker-compose up -d
python demos/etl_invoice_processing/etl_invoice_demo.py
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature description

- Detailed description of changes
- Any breaking changes
- Related issues: #123"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

## 📝 Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for function parameters and return values
- Keep functions focused and under 50 lines when possible
- Use descriptive variable and function names

### Code Example
```python
from typing import Dict, Any, Optional
from .models import Agent, Department

def create_agent(
    role: str,
    job: str,
    tools: Optional[list] = None
) -> Agent:
    """Create a new agent with the specified configuration.
    
    Args:
        role: The agent's role in the workflow
        job: Description of the agent's job
        tools: Optional list of tools the agent can use
        
    Returns:
        Agent: The configured agent instance
    """
    return Agent(
        role=role,
        job=job,
        tools=tools or []
    )
```

### Documentation
- Add docstrings to all public functions and classes
- Use Google-style docstring format
- Include examples in docstrings for complex functions
- Update README.md for user-facing changes

## 🧪 Testing Guidelines

### Writing Tests
- Test both success and failure cases
- Use descriptive test names
- Mock external dependencies
- Test edge cases and error conditions

### Test Example
```python
import pytest
from memra.execution import ExecutionEngine
from memra.models import Agent, Department

def test_execution_engine_creates_audit():
    """Test that execution engine creates audit records."""
    # Arrange
    engine = ExecutionEngine()
    agent = Agent(role="Test", job="Test job")
    department = Department(
        name="Test",
        agents=[agent],
        workflow_order=["Test"]
    )
    
    # Act
    result = engine.execute_department(department, {})
    
    # Assert
    assert result.success
    assert engine.last_execution_audit is not None
    assert "Test" in engine.last_execution_audit.agents_run
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_execution.py

# Run tests with verbose output
pytest -v

# Run tests and show coverage
pytest --cov=memra --cov-report=html
```

## 📚 Documentation

### When to Update Documentation
- New features or API changes
- Bug fixes that affect behavior
- New examples or demos
- Configuration changes

### Documentation Files
- **README.md**: Main project overview and quick start
- **QUICK_START.md**: 5-minute setup guide
- **TEAM_SETUP.md**: Detailed development setup
- **docs/**: Additional technical documentation
- **examples/**: Code examples with comments
- **demos/**: Comprehensive workflow demonstrations

## 🚀 Release Process

### 1. Version Bump
```bash
# Update version in pyproject.toml
# Example: version = "0.2.4" -> version = "0.2.5"
```

### 2. Update Changelog
```bash
# Add entry to CHANGELOG.md
# Include new features, bug fixes, and breaking changes
```

### 3. Build and Test
```bash
# Build the package
python -m build

# Test the build
pip install dist/memra-*.whl
python -c "import memra; print(memra.__version__)"
```

### 4. Publish to PyPI
```bash
# Upload to PyPI
twine upload dist/memra-*

# Tag the release
git tag v0.2.5
git push origin v0.2.5
```

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues for duplicates
2. Try the latest version from PyPI
3. Test with a fresh environment
4. Include minimal reproduction steps

### Bug Report Template
```markdown
**Description**
Brief description of the issue

**Steps to Reproduce**
1. Install memra: `pip install memra`
2. Run: `python examples/simple_example.py`
3. See error: [paste error message]

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: macOS 12.0
- Python: 3.11.0
- Memra: 0.2.4
- Docker: 20.10.0

**Additional Context**
Any other relevant information
```

## 💡 Feature Requests

### Before Requesting
1. Check if the feature already exists
2. Consider if it fits the project scope
3. Think about implementation complexity
4. Consider backward compatibility

### Feature Request Template
```markdown
**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How should this feature work?

**Alternative Solutions**
Other ways to solve this problem

**Additional Context**
Any other relevant information
```

## 🤝 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear and descriptive

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Demo runs successfully
- [ ] No breaking changes to existing functionality

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🆘 Getting Help

### Resources
- **Documentation**: Check `docs/` directory and README files
- **Examples**: See `examples/` and `demos/` directories
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions

### Contact
- **Technical Issues**: Create a GitHub issue
- **General Questions**: Use GitHub Discussions
- **Security Issues**: Email hello@memra.co

## 📋 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Report any inappropriate behavior

## 🎉 Thank You!

Thank you for contributing to Memra! Your contributions help make the framework better for everyone. Whether you're fixing bugs, adding features, or improving documentation, every contribution is valuable.

Happy coding! 🚀 
