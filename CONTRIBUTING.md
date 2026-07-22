# Contributing to Universal Media Downloader

Thank you for your interest in contributing to Universal Media Downloader! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Workflow](#contributing-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## 🤝 Code of Conduct

This project adheres to a standard code of conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences
- Accept responsibility and apologize for mistakes

## 🚀 Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of the [repository page](https://github.com/yourusername/universal-media-downloader).

### 2. Clone Your Fork

```bash
git clone https://github.com/yourusername/universal-media-downloader.git
cd universal-media-downloader
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/originalowner/universal-media-downloader.git
```

## 💻 Development Setup

### Prerequisites

- Python 3.10, 3.11, or 3.12
- FFmpeg installed and in PATH
- yt-dlp installed and in PATH
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy pre-commit

# 5. Install pre-commit hooks
pre-commit install

# 6. Copy environment configuration
cp .env.example .env

# 7. Verify setup
pytest tests/ -v
```

### Verify Installation

```bash
# Run tests
pytest tests/ -v

# Check code quality
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ --count --max-complexity=10 --max-line-length=100
mypy src/ --strict --ignore-missing-imports
```

## 🔄 Contributing Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
# Update your fork
git fetch upstream
git merge upstream/main

# Create feature branch
git checkout -b feature/amazing-feature

# Or for bug fixes
git checkout -b fix/bug-description

# Or for documentation
git checkout -b docs/update-readme
```

**Branch Naming Convention:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests
- `chore/` - Maintenance tasks

### 2. Make Your Changes

Follow the [Code Standards](#code-standards) below.

### 3. Test Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/ --cov-report=html

# Run specific test
pytest tests/unit/test_media_request.py -v
```

### 4. Format Your Code

```bash
# Format with Black
black src/ tests/

# Sort imports
isort src/ tests/

# Check with Flake8
flake8 src/ --count --max-complexity=10 --max-line-length=100

# Type check
mypy src/ --strict --ignore-missing-imports
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add amazing feature"
```

See [Commit Guidelines](#commit-guidelines) for commit message format.

### 6. Push to Your Fork

```bash
git push origin feature/amazing-feature
```

### 7. Open a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template
5. Submit for review

## 📏 Code Standards

### Python Style Guide

This project follows **PEP 8** with these specific rules:

- **Line Length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes preferred (Black will enforce)
- **Type Hints**: Required on all functions and methods
- **Docstrings**: Required for all public classes and functions

### Type Hints Example

```python
from typing import Optional
from uuid import UUID

async def get_download_status(
    request_id: str,
    include_metadata: bool = False,
) -> Optional[DownloadStatus]:
    """Retrieve the status of a download request.
    
    Args:
        request_id: The unique identifier of the download.
        include_metadata: Whether to include full metadata.
    
    Returns:
        The download status if found, None otherwise.
    
    Raises:
        DownloadNotFoundError: If the request doesn't exist.
    """
    pass
```

### Docstring Format

Use **Google-style** docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of what the function does.
    
    Longer description if needed, explaining the purpose
    and any important details.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: When param1 is invalid.
        TypeError: When param2 has wrong type.
    
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### Class Naming

```python
# ✅ Good
class MediaRequest:
    """Domain entity for download requests."""
    pass

class CreateDownloadRequestUseCase:
    """Use case for creating download requests."""
    pass

# ❌ Bad
class media_request:
    pass

class CreateDLRequestUC:
    pass
```

### Function Naming

```python
# ✅ Good
async def create_download_request(input_dto: CreateDownloadRequestInput) -> CreateDownloadRequestOutput:
    """Create a new download request."""
    pass

async def fetch_metadata(url: str) -> dict:
    """Fetch metadata for a URL."""
    pass

# ❌ Bad
async def create_dl_req(input: CreateDownloadRequestInput) -> CreateDownloadRequestOutput:
    pass

async def get_meta(url: str) -> dict:
    pass
```

### Error Handling

Use the `AppError` hierarchy:

```python
from src.infrastructure.errors.app_errors import (
    ValidationError,
    ResourceNotFoundError,
    ExternalServiceError,
)

# ✅ Good
if not url.startswith(("http://", "https://")):
    raise ValidationError(
        message="URL must start with http:// or https://",
        details={"url": url},
    )

request = await repo.find_by_id(request_id)
if request is None:
    raise ResourceNotFoundError(
        message=f"Download request '{request_id}' not found.",
        resource_type="download_request",
        resource_id=request_id,
    )

# ❌ Bad
if not url.startswith(("http://", "https://")):
    raise ValueError("Invalid URL")

if request is None:
    print(f"Request {request_id} not found")
    return None
```

### Architecture Rules

**Strictly enforce Clean Architecture:**

1. **Domain layer** must have ZERO imports from infrastructure or presentation
2. **Infrastructure** can import from domain
3. **Presentation** can import from both domain and infrastructure
4. **Dependencies flow inward only**

```python
# ✅ Good - Domain has no external dependencies
# src/domain/entities/media_request.py
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

# ❌ Bad - Domain importing from infrastructure
# src/domain/entities/media_request.py
from src.infrastructure.logging.logger import get_logger  # NEVER DO THIS
```

## 🧪 Testing Requirements

### Test Coverage

- **Minimum Coverage**: 80% (aim for 95%+)
- **All use cases** must have tests
- **All entities** must have validation tests
- **All endpoints** should have integration tests

### Test Structure

```python
"""Unit tests for [Component Name]."""

import pytest

from src.domain.entities.media_request import MediaRequest
from src.domain.use_cases.create_download_request import CreateDownloadRequestUseCase


class MockRepository:
    """Mock repository for testing."""
    pass


@pytest.mark.asyncio
class TestCreateDownloadRequestUseCase:
    """Tests for CreateDownloadRequestUseCase."""

    async def test_create_download_request_success(self) -> None:
        """Test successful creation of a download request."""
        # Arrange
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)
        
        # Act
        result = await use_case.execute(input_dto)
        
        # Assert
        assert result.id is not None
        assert result.status == "queued"

    async def test_create_download_request_invalid_url(self) -> None:
        """Test that invalid URL raises ValueError."""
        # Arrange
        repo = MockRepository()
        use_case = CreateDownloadRequestUseCase(repository=repo)
        
        # Act & Assert
        with pytest.raises(ValueError):
            await use_case.execute(invalid_input_dto)
```

### Test Naming

- Test files: `test_<module_name>.py`
- Test classes: `Test<ComponentName>`
- Test methods: `test_<scenario>_<expected_behavior>`

### Mocking

Use mocks for external dependencies:

```python
class MockDownloader(DownloaderService):
    """Mock downloader for testing."""
    
    def __init__(self) -> None:
        self.should_fail = False
    
    async def download(self, request: MediaRequest) -> str:
        if self.should_fail:
            raise Exception("Download failed")
        return "/path/to/file.mp4"
```

## 📝 Commit Guidelines

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Scopes:**
- `domain`: Domain layer changes
- `infrastructure`: Infrastructure layer changes
- `presentation`: Presentation layer changes
- `api`: API changes
- `web`: Web UI changes
- `tests`: Test changes
- `docs`: Documentation changes

### Examples

```bash
# Feature
git commit -m "feat(api): add URL validation endpoint"

# Bug fix
git commit -m "fix(domain): handle invalid state transitions in MediaRequest"

# Documentation
git commit -m "docs: update installation guide for Windows"

# Refactoring
git commit -m "refactor(infrastructure): extract yt-dlp command building logic"

# Tests
git commit -m "tests(domain): add state transition tests for MediaRequest"

# Multiple changes
git commit -m "feat(api): add download cancellation support

- Add cancel endpoint to download controller
- Implement cancel_download in YtDlpAdapter
- Add tests for cancellation flow
- Update API documentation"
```

## 🔀 Pull Request Process

### 1. PR Requirements

Before opening a PR, ensure:
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Code is formatted (`black src/ tests/`)
- [ ] Imports are sorted (`isort src/ tests/`)
- [ ] No linting errors (`flake8 src/`)
- [ ] Type checking passes (`mypy src/ --strict`)
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventions

### 2. PR Template

When opening a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

### 3. Review Process

1. **Automated Checks**: CI/CD will run tests and quality checks
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any review comments
4. **Approval**: Once approved, a maintainer will merge
5. **Celebration**: 🎉 Your contribution is now part of the project!

### 4. PR Best Practices

- **Keep PRs focused**: One feature/fix per PR
- **Smaller is better**: Break large changes into multiple PRs
- **Descriptive titles**: Clearly state what the PR does
- **Link issues**: Reference related issues (e.g., "Fixes #123")
- **Update docs**: If you change behavior, update documentation

## 🐛 Reporting Issues

### Bug Reports

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

1. **Clear description** of the bug
2. **Steps to reproduce** (numbered list)
3. **Expected behavior** vs **actual behavior**
4. **Environment details**:
   - OS (Windows/macOS/Linux)
   - Python version
   - FFmpeg version
   - yt-dlp version
5. **Logs/error messages** (if applicable)
6. **Screenshots** (if applicable)

### Feature Requests

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

1. **Problem statement**: What problem does this solve?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: Other approaches you've thought about
4. **Use case**: Why is this feature important?

### Questions

For questions and discussions:
- Check existing [documentation](README.md)
- Search [existing issues](https://github.com/yourusername/universal-media-downloader/issues)
- Use [GitHub Discussions](https://github.com/yourusername/universal-media-downloader/discussions)

## 🎯 Priority Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- 🗄️ Database persistence (PostgreSQL, SQLite)
- 🔐 User authentication and authorization
- 📅 Download scheduling and queue management
- 🌐 WebSocket support for real-time progress
- 🧪 Integration tests

### Medium Priority
- 📱 Progressive Web App (PWA) features
- 🌍 Internationalization (i18n)
- 🔌 Plugin system for custom extractors
- 📊 Analytics and usage tracking
- 🎨 UI/UX improvements

### Good First Issues
- 📝 Documentation improvements
- 🐛 Bug fixes
- ✅ Test coverage improvements
- 🎨 UI polish
- 🌐 Translation contributions

## 💡 Tips for Contributors

1. **Start small**: Begin with documentation or small bug fixes
2. **Ask questions**: Don't hesitate to ask for clarification
3. **Read the code**: Understand the architecture before making changes
4. **Write tests**: Tests are not optional
5. **Be patient**: Reviews take time, maintainers are volunteers
6. **Learn together**: We're all here to improve

## 📚 Additional Resources

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp#readme)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)

## 🙏 Recognition

All contributors will be:
- Listed in the README.md contributors section
- Mentioned in release notes for significant contributions
- Given credit in commit messages

Thank you for contributing to Universal Media Downloader! 🎉

---

**Questions?** Open an issue or reach out to the maintainers.