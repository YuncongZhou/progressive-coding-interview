"""
Database ORM - Stage 2

Querying and filtering.

Design Rationale:
- Filter by field values
- Chained queries
- Basic ordering
"""

from typing import Optional, List, Dict, Any, Callable
import uuid


class Field:
    def __init__(self, required: bool = True, default: Any = None):
        self.required = required
        self.default = default
        self.name = ""


class StringField(Field):
    pass


class IntField(Field):
    pass


class BoolField(Field):
    pass


class Query:
    """Query builder for filtering models."""

    def __init__(self, model_class: type, items: List['Model']):
        self._model_class = model_class
        self._items = items

    def filter(self, **kwargs) -> 'Query':
        """Filter by field values."""
        result = []
        for item in self._items:
            match = True
            for key, value in kwargs.items():
                if getattr(item, key, None) != value:
                    match = False
                    break
            if match:
                result.append(item)
        return Query(self._model_class, result)

    def filter_by(self, predicate: Callable[['Model'], bool]) -> 'Query':
        """Filter by custom predicate."""
        return Query(self._model_class, [i for i in self._items if predicate(i)])

    def order_by(self, field: str, descending: bool = False) -> 'Query':
        """Order by field."""
        sorted_items = sorted(self._items, key=lambda x: getattr(x, field, 0),
                              reverse=descending)
        return Query(self._model_class, sorted_items)

    def limit(self, n: int) -> 'Query':
        """Limit results."""
        return Query(self._model_class, self._items[:n])

    def offset(self, n: int) -> 'Query':
        """Skip first n results."""
        return Query(self._model_class, self._items[n:])

    def first(self) -> Optional['Model']:
        """Get first result."""
        return self._items[0] if self._items else None

    def last(self) -> Optional['Model']:
        """Get last result."""
        return self._items[-1] if self._items else None

    def all(self) -> List['Model']:
        """Get all results."""
        return self._items.copy()

    def count(self) -> int:
        """Count results."""
        return len(self._items)

    def exists(self) -> bool:
        """Check if any results exist."""
        return len(self._items) > 0


class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
        namespace['_fields'] = fields
        return super().__new__(mcs, name, bases, namespace)


class Model(metaclass=ModelMeta):
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
        self._get_table()[self.id] = self
        return self

    def delete(self) -> bool:
        table = self._get_table()
        if self.id in table:
            del table[self.id]
            return True
        return False

    @classmethod
    def get(cls, id: str) -> Optional['Model']:
        return cls._get_table().get(id)

    @classmethod
    def query(cls) -> Query:
        """Start a query."""
        return Query(cls, list(cls._get_table().values()))

    @classmethod
    def all(cls) -> List['Model']:
        return list(cls._get_table().values())

    @classmethod
    def count(cls) -> int:
        return len(cls._get_table())

    @classmethod
    def clear(cls) -> None:
        cls._get_table().clear()

    def to_dict(self) -> Dict[str, Any]:
        result = {'id': self.id}
        for name in self._fields:
            result[name] = getattr(self, name)
        return result
