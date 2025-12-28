"""
Database ORM - Stage 3

Relationships between models.

Design Rationale:
- ForeignKey for one-to-many
- Access related objects
- Cascade operations
"""

from typing import Optional, List, Dict, Any, Callable, Type
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


class ForeignKey(Field):
    """Foreign key to another model."""
    def __init__(self, model: str, required: bool = True):
        super().__init__(required=required, default=None)
        self.model_name = model


class Query:
    def __init__(self, model_class: type, items: List['Model']):
        self._model_class = model_class
        self._items = items

    def filter(self, **kwargs) -> 'Query':
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
        return Query(self._model_class, [i for i in self._items if predicate(i)])

    def order_by(self, field: str, descending: bool = False) -> 'Query':
        sorted_items = sorted(self._items, key=lambda x: getattr(x, field, 0),
                              reverse=descending)
        return Query(self._model_class, sorted_items)

    def limit(self, n: int) -> 'Query':
        return Query(self._model_class, self._items[:n])

    def first(self) -> Optional['Model']:
        return self._items[0] if self._items else None

    def all(self) -> List['Model']:
        return self._items.copy()

    def count(self) -> int:
        return len(self._items)


class ModelMeta(type):
    _models: Dict[str, type] = {}

    def __new__(mcs, name, bases, namespace):
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
        namespace['_fields'] = fields
        cls = super().__new__(mcs, name, bases, namespace)
        mcs._models[name] = cls
        return cls


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

    def delete(self, cascade: bool = False) -> bool:
        if cascade:
            self._cascade_delete()
        table = self._get_table()
        if self.id in table:
            del table[self.id]
            return True
        return False

    def _cascade_delete(self) -> None:
        """Delete related objects."""
        for model_name, model_cls in ModelMeta._models.items():
            for fname, field in model_cls._fields.items():
                if isinstance(field, ForeignKey) and field.model_name == self.__class__.__name__:
                    for obj in model_cls.query().filter(**{fname: self.id}).all():
                        obj.delete(cascade=True)

    def get_related(self, model_class: Type['Model'], field_name: str) -> List['Model']:
        """Get objects related to this one."""
        return model_class.query().filter(**{field_name: self.id}).all()

    def get_foreign(self, field_name: str) -> Optional['Model']:
        """Get the foreign object."""
        field = self._fields.get(field_name)
        if not isinstance(field, ForeignKey):
            return None
        fk_id = getattr(self, field_name)
        if fk_id is None:
            return None
        model_cls = ModelMeta._models.get(field.model_name)
        return model_cls.get(fk_id) if model_cls else None

    @classmethod
    def get(cls, id: str) -> Optional['Model']:
        return cls._get_table().get(id)

    @classmethod
    def query(cls) -> Query:
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
