---
name: python-coding-conventions
description: Python coding standards for type safety and maintainability
---

# Python Coding Conventions

Enforce type safety and consistency across the backend codebase through Pydantic objects and strict return types.

## Core Rules

### 1. NEVER Return `dict` or `list[dict]`

**❌ WRONG:**
```python
def get_user(user_id: str) -> dict:
    """Get user by ID."""
    return {"id": user.id, "username": user.username}

def list_users() -> list[dict]:
    """List all users."""
    return [{"id": u.id, "username": u.username} for u in users]
```

**✅ CORRECT:**
```python
def get_user(user_id: str) -> UserDTO:
    """Get user by ID."""
    return UserDTO(**user.model_dump())

def list_users() -> list[UserDTO]:
    """List all users."""
    return [UserDTO(**u.model_dump()) for u in users]
```

### 2. Always Use Pydantic Objects as Return Types

All functions that return structured data must use Pydantic DTO objects, not dictionaries.

**Rules:**
- Services return Pydantic DTOs
- Dependencies return Pydantic DTOs
- Routers return Pydantic DTOs (FastAPI response_model handles serialization)
- Never unpack Pydantic objects into dicts for return values

**Example Service:**
```python
from shared.dtos.core.auth_dtos import SafeUserDTO

class AuthService:
    def validate_session(self, session_id: str) -> SafeUserDTO:
        """Validate session and return user."""
        session_record = self.session_repo.get_valid_session(session_id)
        user = self.user_repo.get_by_id(session_record.user_id)
        return SafeUserDTO(**user.model_dump())  # ✅ Return DTO, not dict
```

**Example Dependency:**
```python
from shared.dtos.core.auth_dtos import SafeUserDTO

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db_session),
) -> SafeUserDTO:  # ✅ Return SafeUserDTO, not dict
    """Validate and return current user."""
    auth_service = AuthService(session)
    return auth_service.validate_session(credentials.credentials)
```

**Example Router:**
```python
def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserDTO:  # ✅ FastAPI handles serialization
    """Get user by ID."""
    return service.get_by_id(user_id)  # Returns UserDTO directly
```

### 3. Converting Database Models to DTOs

When converting SQLModel/database objects to DTOs:

**✅ CORRECT:**
```python
# Extract only needed fields explicitly
safe_user = SafeUserDTO(
    id=user.id,
    username=user.username,
    full_name=user.full_name,
)

# Or use model_dump() with exclude for sensitive fields
safe_user = SafeUserDTO(**user.model_dump(exclude={"password_hash"}))

# Or use model_dump() directly when DTO fields match model fields
user_dto = UserDTO(**user.model_dump())
```

**❌ WRONG:**
```python
# Don't return dicts from model data
return {
    "id": user.id,
    "username": user.username,
}

# Don't try to return the database model directly
return user  # ❌ Database model, not DTO
```

### 4. Type Hints for Return Values

Always specify return types explicitly:

**✅ CORRECT:**
```python
def get_user(user_id: str) -> UserDTO:
    ...

def list_users() -> list[UserDTO]:
    ...

def search_users(query: str) -> UsersListResponseDTO:
    ...
```

**❌ WRONG:**
```python
def get_user(user_id: str):  # ❌ No return type
    ...

def get_user(user_id: str) -> dict:  # ❌ Too generic
    ...

def list_users() -> list:  # ❌ Not typed properly
    ...
```

### 5. When to Create New DTOs

Create DTOs when:
- Returning data from functions/methods
- Request bodies for API endpoints
- Response bodies for API endpoints
- Dependency injection returns

**Example:**
```python
# Create SafeUserDTO for functions that return user data
# without password_hash
class SafeUserDTO(BaseDTO):
    id: str = Field(...)
    username: str = Field(...)
    full_name: str = Field(...)

# Use this in services and dependencies
def validate_session(self, session_id: str) -> SafeUserDTO:
    ...

# Use in dependencies
def get_current_user(...) -> SafeUserDTO:
    ...
```

## Why These Rules Matter

### Type Safety
- Type checkers (mypy, pyright) can verify your code
- IDEs provide better autocomplete
- Runtime validation via Pydantic

### API Consistency
- All endpoints return consistent, documented structures
- OpenAPI/Swagger automatically documents response schemas
- Frontend type generation works correctly

### Data Security
- DTOs can exclude sensitive fields (passwords, tokens, etc.)
- Clear control over what data is serialized

### Maintainability
- Clear contracts between layers (service → router → API)
- Changes to data structures are caught by type checker
- Self-documenting code

## Common Patterns

### List Responses (CRITICAL)

Never return raw lists from API endpoints:

**✅ CORRECT:**
```python
class UsersListResponseDTO(BaseDTO):
    items: list[UserDTO] = Field(...)
    total: int = Field(...)

@router.get("/users")
def list_users(service: UserService = Depends(...)) -> UsersListResponseDTO:
    users = service.list_all()
    return UsersListResponseDTO(items=users, total=len(users))
```

**❌ WRONG:**
```python
@router.get("/users")
def list_users(service: UserService = Depends(...)) -> list[UserDTO]:
    return service.list_all()  # ❌ Raw list, no metadata
```

### Optional Fields

Use `Optional` for nullable fields:

```python
class UserDTO(BaseDTO):
    id: str = Field(...)
    username: str = Field(...)
    bio: Optional[str] = Field(default=None, description="User bio")
```

### Sensitive Data

Create Safe DTOs that exclude sensitive fields:

```python
# Full user model (database layer)
class User(SQLModel, table=True):
    id: str
    username: str
    password_hash: str  # ❌ Never expose this
    email: str

# Full DTO for internal services
class UserDTO(BaseDTO):
    id: str
    username: str
    email: str
    # password_hash intentionally excluded

# Safe DTO for public APIs
class SafeUserDTO(BaseDTO):
    id: str
    username: str
    # email also excluded from public DTO
```

## Checklist for Code Review

- [ ] All functions have explicit return types
- [ ] No functions return `dict` or `list[dict]`
- [ ] All functions return Pydantic objects or basic types (str, int, bool)
- [ ] Services return DTOs, not database models
- [ ] Dependencies return DTOs, not dicts
- [ ] Routers use DTOs for responses
- [ ] List endpoints return wrapper objects with `items` and `total` fields
- [ ] Sensitive fields excluded from public DTOs
- [ ] Type hints match actual return values
