"""
Database ORM - Stage 1

Basic ORM with models and CRUD.

Design Rationale:
- Define models with fields
- Basic CRUD operations
- In-memory storage
"""

from typing import Optional, List, Dict, Any, Type
from dataclasses import dataclass, field
import uuid


class Field:
    """Base field type."""
    def __init__(self, required: bool = True, default: Any = None):
        self.required = required
        self.default = default
        self.name = ""  # Set by Model metaclass


class StringField(Field):
    """String field type."""
    pass


class IntField(Field):
    """Integer field type."""
    pass


class BoolField(Field):
    """Boolean field type."""
    pass


class ModelMeta(type):
    """Metaclass for Model to collect fields."""
    def __new__(mcs, name, bases, namespace):
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value

        namespace['_fields'] = fields
        return super().__new__(mcs, name, bases, namespace)


class Model(metaclass=ModelMeta):
    """Base model class."""
    _storage: Dict[str, Dict[str, 'Model']] = {}
    _fields: Dict[str, Field] = {}

    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', str(uuid.uuid4())[:8])

        for name, field in self._fields.items():
            value = kwargs.get(name, field.default)
            if value is None and field.required:
                raise ValueError(f"Field '{name}' is required")
            setattr(self, name, value)

    @classmethod
    def _get_table(cls) -> Dict[str, 'Model']:
        table_name = cls.__name__
        if table_name not in cls._storage:
            cls._storage[table_name] = {}
        return cls._storage[table_name]

    def save(self) -> 'Model':
        """Save model to storage."""
        self._get_table()[self.id] = self
        return self

    def delete(self) -> bool:
        """Delete model from storage."""
        table = self._get_table()
        if self.id in table:
            del table[self.id]
            return True
        return False

    @classmethod
    def get(cls, id: str) -> Optional['Model']:
        """Get model by ID."""
        return cls._get_table().get(id)

    @classmethod
    def all(cls) -> List['Model']:
        """Get all models."""
        return list(cls._get_table().values())

    @classmethod
    def count(cls) -> int:
        """Count all models."""
        return len(cls._get_table())

    @classmethod
    def clear(cls) -> None:
        """Clear all models."""
        cls._get_table().clear()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {'id': self.id}
        for name in self._fields:
            result[name] = getattr(self, name)
        return result
