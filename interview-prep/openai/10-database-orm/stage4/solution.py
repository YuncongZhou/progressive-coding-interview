"""
Database ORM - Stage 4

Validation and hooks.

Design Rationale:
- Field validation
- Pre/post save hooks
- Schema validation
"""

from typing import Optional, List, Dict, Any, Callable, Type
import uuid
import re


class ValidationError(Exception):
    """Validation error."""
    pass


class Field:
    def __init__(self, required: bool = True, default: Any = None,
                 validators: List[Callable] = None):
        self.required = required
        self.default = default
        self.validators = validators or []
        self.name = ""

    def validate(self, value: Any) -> None:
        """Validate field value."""
        for validator in self.validators:
            validator(value)


class StringField(Field):
    def __init__(self, min_length: int = 0, max_length: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None:
            if not isinstance(value, str):
                raise ValidationError(f"{self.name} must be a string")
            if len(value) < self.min_length:
                raise ValidationError(f"{self.name} too short")
            if self.max_length and len(value) > self.max_length:
                raise ValidationError(f"{self.name} too long")


class IntField(Field):
    def __init__(self, min_value: int = None, max_value: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None:
            if not isinstance(value, int):
                raise ValidationError(f"{self.name} must be an integer")
            if self.min_value is not None and value < self.min_value:
                raise ValidationError(f"{self.name} too small")
            if self.max_value is not None and value > self.max_value:
                raise ValidationError(f"{self.name} too large")


class EmailField(StringField):
    def validate(self, value: Any) -> None:
        super().validate(value)
        if value is not None:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                raise ValidationError(f"{self.name} is not a valid email")


class ForeignKey(Field):
    def __init__(self, model: str, required: bool = True):
        super().__init__(required=required, default=None)
        self.model_name = model


class Query:
    def __init__(self, model_class: type, items: List['Model']):
        self._model_class = model_class
        self._items = items

    def filter(self, **kwargs) -> 'Query':
        result = [i for i in self._items
                  if all(getattr(i, k, None) == v for k, v in kwargs.items())]
        return Query(self._model_class, result)

    def order_by(self, field: str, descending: bool = False) -> 'Query':
        return Query(self._model_class,
                     sorted(self._items, key=lambda x: getattr(x, field, 0),
                            reverse=descending))

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
        self._is_new = True

        for name, field in self._fields.items():
            value = kwargs.get(name, field.default)
            if value is None and field.required:
                raise ValueError(f"Field '{name}' is required")
            setattr(self, name, value)

    def validate(self) -> None:
        """Validate all fields."""
        for name, field in self._fields.items():
            value = getattr(self, name)
            field.validate(value)

    def _pre_save(self) -> None:
        """Hook called before save."""
        pass

    def _post_save(self) -> None:
        """Hook called after save."""
        pass

    def _pre_delete(self) -> None:
        """Hook called before delete."""
        pass

    @classmethod
    def _get_table(cls) -> Dict[str, 'Model']:
        table_name = cls.__name__
        if table_name not in cls._storage:
            cls._storage[table_name] = {}
        return cls._storage[table_name]

    def save(self, validate: bool = True) -> 'Model':
        """Save with validation and hooks."""
        if validate:
            self.validate()
        self._pre_save()
        self._get_table()[self.id] = self
        was_new = self._is_new
        self._is_new = False
        self._post_save()
        return self

    def delete(self, cascade: bool = False) -> bool:
        self._pre_delete()
        if cascade:
            self._cascade_delete()
        table = self._get_table()
        if self.id in table:
            del table[self.id]
            return True
        return False

    def _cascade_delete(self) -> None:
        for model_name, model_cls in ModelMeta._models.items():
            for fname, field in model_cls._fields.items():
                if isinstance(field, ForeignKey) and field.model_name == self.__class__.__name__:
                    for obj in model_cls.query().filter(**{fname: self.id}).all():
                        obj.delete(cascade=True)

    def get_related(self, model_class: Type['Model'], field_name: str) -> List['Model']:
        return model_class.query().filter(**{field_name: self.id}).all()

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

    @property
    def is_new(self) -> bool:
        """Check if model hasn't been saved yet."""
        return self._is_new
