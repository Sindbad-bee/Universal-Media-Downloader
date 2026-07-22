# Universal Media Downloader - Architecture Documentation

## Table of Contents

- [Overview](#overview)
- [Clean Architecture Principles](#clean-architecture-principles)
- [Layer Breakdown](#layer-breakdown)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [State Machine](#state-machine)
- [Dependency Injection](#dependency-injection)
- [Error Handling Strategy](#error-handling-strategy)
- [Logging Strategy](#logging-strategy)

## Overview

Universal Media Downloader is built using **Clean Architecture** (also known as Hexagonal Architecture or Ports and Adapters). This architectural style ensures the system is:

- **Framework-independent**: Business logic doesn't depend on FastAPI, Pydantic, or any other framework
- **Testable**: Easy to unit test with mocked dependencies
- **Maintainable**: Clear separation of concerns makes the codebase easy to understand and modify
- **Flexible**: Easy to swap implementations (e.g., replace in-memory repository with PostgreSQL)

## Clean Architecture Principles

### The Dependency Rule

**Source code dependencies can only point inward.** This means:

- The Domain layer has zero dependencies on external frameworks
- The Infrastructure layer depends on the Domain layer
- The Presentation layer depends on both Domain and Infrastructure layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  (FastAPI, Pydantic DTOs, HTML/CSS/JS)                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dependencies: Domain + Infrastructure                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ depends on
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  (yt-dlp adapter, FFmpeg wrapper, Logging, Repositories)    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dependencies: Domain only                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ depends on
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                             │
│  (Entities, Use Cases, Repository Interfaces)                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dependencies: Nothing (pure Python)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Benefits

1. **Framework Independence**: You can replace FastAPI with Flask, Django, or any other framework without changing business logic
2. **Testability**: Domain logic can be tested without databases, web servers, or external services
3. **Maintainability**: Clear boundaries make it easy to locate and fix bugs
4. **Flexibility**: Easy to add new adapters (e.g., different downloaders, different databases)

## Layer Breakdown

### 1. Domain Layer (`src/domain/`)

**Purpose**: Contains the core business logic and rules. This is the heart of the application.

**Components**:

#### Entities (`entities/`)
- **MediaRequest**: The central domain entity representing a download request
  - Contains business rules (URL validation, state transitions)
  - State machine: PENDING → QUEUED → IN_PROGRESS → COMPLETED/FAILED/CANCELLED
  - Zero dependencies on external frameworks

**Key Characteristics**:
- Pure Python dataclasses and enums
- No imports from infrastructure or presentation
- Business validation in `__post_init__`
- State transition methods with validation

#### Interfaces (`interfaces/`)
- **MediaRepository**: Abstract interface for data persistence
  - Methods: `save`, `find_by_id`, `find_all`, `delete`, `count`
  - Implementations belong in infrastructure layer
  
- **DownloaderService**: Abstract interface for media downloading
  - Methods: `fetch_metadata`, `download`, `cancel_download`, `validate_url`
  - Implementations belong in infrastructure layer

**Key Characteristics**:
- Abstract base classes (ABC)
- Define contracts only, no implementation
- Use async methods for I/O operations

#### Use Cases (`use_cases/`)
- **CreateDownloadRequestUseCase**: Creates a new download request
- **ExecuteDownloadUseCase**: Executes a download operation
- **GetDownloadStatusUseCase**: Retrieves download status
- **ListDownloadsUseCase**: Lists all downloads with pagination

**Key Characteristics**:
- Orchestrate business operations
- Depend only on interfaces (dependency inversion)
- Return DTOs (data transfer objects)
- No knowledge of HTTP, databases, or external services

### 2. Infrastructure Layer (`src/infrastructure/`)

**Purpose**: Implements interfaces defined in the domain layer. Handles external concerns.

**Components**:

#### Adapters (`adapters/`)
- **YtDlpAdapter**: Implements `DownloaderService`
  - Wraps yt-dlp CLI tool via asyncio subprocess
  - Handles process management, timeouts, and error parsing
  - Builds complex yt-dlp command-line arguments
  
- **InMemoryMediaRepository**: Implements `MediaRepository`
  - Thread-safe in-memory storage
  - Deep copy protection against mutation
  - Pagination support

**Key Characteristics**:
- Can import from domain layer
- Handle external service integration
- Manage resources (processes, file handles, connections)
- Convert between domain entities and external formats

#### Errors (`errors/`)
- **AppError**: Base exception class
- **ValidationError**: Input validation failures
- **ResourceNotFoundError**: Missing resources
- **ExternalServiceError**: yt-dlp/FFmpeg failures
- **DownloaderAdapterError**: yt-dlp specific errors
- **DownloadExecutionError**: Download operation failures
- **FileSystemError**: File system operation failures
- **RepositoryError**: Data persistence failures

**Key Characteristics**:
- Hierarchical error structure
- Consistent error response format
- HTTP status code mapping
- Structured error details

#### Logging (`logging/`)
- **AppLogger**: Wrapper around Loguru
  - Structured logging with context
  - Console and file handlers
  - Log rotation and compression
  - Configurable log levels

**Key Characteristics**:
- Singleton pattern for loggers
- Context-rich log entries
- Performance optimized

### 3. Presentation Layer (`src/presentation/`)

**Purpose**: Handles user interaction and API exposure.

**Components**:

#### Application Factory (`app.py`)
- **create_app()**: FastAPI application factory
- **lifespan()**: Startup and shutdown logic
- **Dependency injection**: Provides singleton services

**Key Characteristics**:
- Factory pattern for app creation
- Lifespan management for resource initialization/cleanup
- Middleware registration
- Static file serving for web UI

#### API Controllers (`api/controllers/`)
- **DownloadController**: Defines HTTP endpoints
  - POST /downloads - Create download request
  - GET /downloads/{id} - Get status
  - POST /downloads/{id}/execute - Execute download
  - GET /downloads - List downloads
  - POST /downloads/{id}/cancel - Cancel download
  - POST /validate-url - Validate URL
  - GET /metadata - Fetch metadata
  - GET /health - Health check

**Key Characteristics**:
- Thin controllers (delegate to use cases)
- Request/response DTOs
- HTTP-specific error handling
- OpenAPI documentation

#### DTOs (`api/dtos/`)
- Pydantic models for request/response validation
- Type-safe API contracts
- Automatic OpenAPI schema generation

#### Middleware (`api/middleware/`)
- **ErrorHandlerMiddleware**: Catches AppError exceptions
- **LoggingMiddleware**: Logs all requests with timing

#### Web UI (`web/`)
- **index.html**: Single-page application
- **styles.css**: Modern, responsive CSS with dark/light themes
- **app.js**: Vanilla JavaScript for API interaction

**Key Characteristics**:
- No framework dependencies (vanilla JS)
- REST API client
- Real-time status polling
- Responsive design

## Data Flow

### Creating a Download Request

```
1. User enters URL in Web UI
   ↓
2. Web UI sends POST /api/v1/downloads
   ↓
3. DownloadController receives request
   ↓
4. Controller creates CreateDownloadRequestInput DTO
   ↓
5. Controller calls CreateDownloadRequestUseCase.execute()
   ↓
6. Use case validates input and creates MediaRequest entity
   ↓
7. Entity validates URL in __post_init__
   ↓
8. Use case calls request.mark_queued() (state transition)
   ↓
9. Use case calls repository.save(request)
   ↓
10. Repository persists the request
   ↓
11. Use case returns CreateDownloadRequestOutput DTO
   ↓
12. Controller returns DownloadRequestResponse DTO
   ↓
13. Web UI displays success message
```

### Executing a Download

```
1. User clicks "Download" button
   ↓
2. Web UI sends POST /api/v1/downloads/{id}/execute
   ↓
3. DownloadController receives request
   ↓
4. Controller calls ExecuteDownloadUseCase.execute()
   ↓
5. Use case retrieves request from repository
   ↓
6. Use case calls request.mark_in_progress()
   ↓
7. Use case calls downloader.download(request)
   ↓
8. YtDlpAdapter builds yt-dlp command
   ↓
9. YtDlpAdapter executes subprocess
   ↓
10. yt-dlp downloads media
   ↓
11. YtDlpAdapter returns file path
   ↓
12. Use case calls request.mark_completed(path)
   ↓
13. Use case saves updated request
   ↓
14. Use case returns ExecuteDownloadOutput DTO
   ↓
15. Controller returns DownloadStatusResponse DTO
   ↓
16. Web UI polls for status updates
```

## Design Patterns

### 1. Repository Pattern

**Purpose**: Abstract data persistence logic.

**Implementation**:
- `MediaRepository` interface in domain layer
- `InMemoryMediaRepository` implementation in infrastructure layer
- Future: `PostgreSQLMediaRepository`, `SQLiteMediaRepository`

**Benefits**:
- Business logic doesn't know about database details
- Easy to swap storage implementations
- Testable with mock repositories

### 2. Service Layer Pattern

**Purpose**: Encapsulate business logic.

**Implementation**:
- `DownloaderService` interface in domain layer
- `YtDlpAdapter` implementation in infrastructure layer
- Future: `Aria2cAdapter`, `WgetAdapter`

**Benefits**:
- Business logic isolated from external tools
- Easy to add new download engines
- Testable with mock services

### 3. Use Case Pattern

**Purpose**: Orchestrate business operations.

**Implementation**:
- Each use case is a separate class
- Input/Output DTOs for type safety
- Depends on interfaces, not implementations

**Benefits**:
- Single responsibility per use case
- Easy to test and maintain
- Clear API for presentation layer

### 4. Dependency Injection

**Purpose**: Invert control of dependency creation.

**Implementation**:
- Use cases receive dependencies via constructor
- FastAPI Depends() for controller-level DI
- Singleton services in app factory

**Benefits**:
- Loose coupling
- Easy to test with mocks
- Centralized dependency management

### 5. Factory Pattern

**Purpose**: Create complex objects with a single interface.

**Implementation**:
- `create_app()` factory function
- Creates and configures FastAPI app
- Initializes singleton services

**Benefits**:
- Consistent app creation
- Easy to create test instances
- Configuration in one place

### 6. DTO Pattern

**Purpose**: Transfer data between layers.

**Implementation**:
- Input DTOs: `CreateDownloadRequestInput`, `ExecuteDownloadInput`
- Output DTOs: `CreateDownloadRequestOutput`, `DownloadStatusResponse`
- Pydantic models for API layer

**Benefits**:
- Type safety
- Validation at boundaries
- Clear contracts between layers

## State Machine

The `MediaRequest` entity implements a state machine for download lifecycle:

```
                    ┌─────────┐
                    │ PENDING │
                    └────┬────┘
                         │ mark_queued()
                         ▼
                    ┌─────────┐
                    │ QUEUED  │
                    └────┬────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │ CANCEL   │  │ IN_      │  │ (direct  │
     │          │  │ PROGRESS │  │  cancel) │
     └──────────┘  └────┬─────┘  └──────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │ COMPLETED│ │  FAILED  │ │ CANCELLED│
     └──────────┘ └──────────┘ └──────────┘
```

**State Transition Rules**:
- PENDING → QUEUED (via `mark_queued()`)
- QUEUED → IN_PROGRESS (via `mark_in_progress()`)
- QUEUED → CANCELLED (via `cancel()`)
- IN_PROGRESS → COMPLETED (via `mark_completed(path)`)
- IN_PROGRESS → FAILED (via `mark_failed(error)`)
- IN_PROGRESS → CANCELLED (via `cancel()`)
- Terminal states (COMPLETED, FAILED, CANCELLED) cannot transition

**Invalid transitions raise `InvalidStateTransitionError`**

## Dependency Injection

### Application Level

```python
# src/presentation/app.py

# Singleton instances
_repository: InMemoryMediaRepository
_downloader: YtDlpAdapter

def get_repository() -> InMemoryMediaRepository:
    global _repository
    return _repository

def get_downloader() -> YtDlpAdapter:
    global _downloader
    return _downloader
```

### Controller Level

```python
# src/presentation/api/controllers/download_controller.py

def _get_create_use_case(
    repo: InMemoryMediaRepository = Depends(_get_repository),
) -> CreateDownloadRequestUseCase:
    return CreateDownloadRequestUseCase(repository=repo)

@router.post("/downloads")
async def create_download(
    body: CreateDownloadRequest,
    use_case: CreateDownloadRequestUseCase = Depends(_get_create_use_case),
):
    # use_case is injected by FastAPI
    pass
```

### Use Case Level

```python
# src/domain/use_cases/execute_download.py

class ExecuteDownloadUseCase:
    def __init__(
        self,
        repository: MediaRepository,      # Interface
        downloader: DownloaderService,     # Interface
    ) -> None:
        self._repository = repository
        self._downloader = downloader
```

**Benefits**:
- Dependencies provided from outside
- Easy to swap implementations
- Testable with mocks

## Error Handling Strategy

### Centralized Error Hierarchy

```
AppError (base)
├── ConfigurationError
├── ValidationError (422)
├── ResourceNotFoundError (404)
├── ExternalServiceError (502)
│   └── DownloaderAdapterError
├── DownloadExecutionError (500)
├── FileSystemError (500)
└── RepositoryError (500)
```

### Error Flow

```
1. Domain/Infrastructure raises AppError subclass
   ↓
2. ErrorHandlerMiddleware catches AppError
   ↓
3. Middleware logs error with context
   ↓
4. Middleware returns structured JSON response
   ↓
5. Client receives consistent error format
```

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "URL must start with http:// or https://",
    "details": {
      "url": "invalid-url"
    }
  }
}
```

### Error Handling Rules

1. **Domain layer**: Raise domain-specific exceptions (ValueError, InvalidStateTransitionError)
2. **Use cases**: Catch domain exceptions, convert to AppError
3. **Infrastructure**: Raise AppError subclasses
4. **Controllers**: Catch use case exceptions, convert to AppError
5. **Middleware**: Catch all AppError, return JSON response

## Logging Strategy

### Structured Logging

All logs use structured format with context:

```python
logger.info(
    "Download started",
    request_id=request.id,
    url=request.url,
    media_type=request.media_type.name,
)
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages (failures that don't stop the app)
- **CRITICAL**: Critical failures

### Log Destinations

1. **Console**: Colorized output for development
2. **File**: Rotating file logs for production
   - Rotation: 10 MB per file
   - Retention: 30 days
   - Compression: gzip

### Log Context

Every log entry includes:
- Timestamp
- Log level
- Module/function/line
- Message
- Structured context (key-value pairs)

### Example Log Output

```
2024-01-15 14:32:45.123 | INFO     | app:lifespan:67 | Application started successfully
2024-01-15 14:32:46.456 | INFO     | yt_dlp_adapter:download:168 | Starting download
    request_id="abc123"
    url="https://youtube.com/watch?v=..."
    command="yt-dlp --no-warnings ..."
```

## Performance Considerations

### Async I/O

- All I/O operations use async/await
- Non-blocking subprocess execution
- Concurrent request handling

### Resource Management

- Active process tracking for cancellation
- Proper cleanup in finally blocks
- Connection pooling for subprocesses

### Caching

- Settings loaded once (lru_cache)
- Logger instances cached
- Singleton services

### Scalability

- Horizontal scaling via multiple workers
- Stateless design (except in-memory storage)
- Docker containerization for deployment

---

**Last Updated**: 2024
**Maintained By**: Universal Media Downloader Contributors