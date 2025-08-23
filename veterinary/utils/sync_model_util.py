from django.db import transaction

import logging
from typing import Callable, Iterable, Tuple, Type, Any, Optional
from django.db import models, transaction

logger = logging.getLogger(__name__)

def sync_model(
    model: Type[models.Model],
    source_objects: Iterable[Any],
    key_fn: Callable[[Any], Any],
    map_fn: Callable[[Any], models.Model],
    update_fields: Optional[list[str]] = None,
    batch_size: int = 1000,
    using: Optional[str] = None,
    key_field: str = "id",
) -> Tuple[int, int]:
    """
    Synchronize source data into a Django model with insert/update behavior.

    Args:
        model (Type[models.Model]): Target Django model.
        source_objects (Iterable[Any]): Source objects to sync.
        key_fn (Callable[[Any], Any]): Function that returns a unique key per source object.
        map_fn (Callable[[Any], models.Model]): Function that maps source object to model instance.
        update_fields (list[str], optional): Fields to update on existing records. Default is None (all updatable fields).
        batch_size (int): Batch size for bulk operations.
        using (str, optional): Database alias if syncing to a non-default database.
        key_field (str): Field name used to identify uniqueness in the target model.

    Returns:
        Tuple[int, int]: Number of records created and updated.
    """

    if not source_objects:
        logger.info(f"No source objects found for model {model.__name__}")
        return 0, 0

    db = using or 'default'
    created_count = 0
    updated_count = 0

    # Create a map of source objects using their unique key
    source_map = {}
    for obj in source_objects:
        key = key_fn(obj)
        if key is not None:
            source_map[key] = obj

    keys = list(source_map.keys())

    # Fetch all existing records corresponding to the keys
    existing_objects = list(model.objects.using(db).filter(**{f"{key_field}__in": keys}))
    key_to_existing = {getattr(obj, key_field): obj for obj in existing_objects}

    to_create = []
    to_update = []

    for key, source in source_map.items():
        if key in key_to_existing:
            instance = key_to_existing[key]
            new_instance = map_fn(source)
            new_instance.pk = instance.pk

            if update_fields:
                for field in update_fields:
                    setattr(instance, field, getattr(new_instance, field))
            to_update.append(instance)
        else:
            to_create.append(map_fn(source))

    with transaction.atomic(using=db):
        if to_create:
            model.objects.using(db).bulk_create(to_create, batch_size=batch_size)
            created_count = len(to_create)

        if to_update and update_fields:
            model.objects.using(db).bulk_update(to_update, update_fields, batch_size=batch_size)
            updated_count = len(to_update)

    logger.info(f"{model.__name__} Sync Complete: Created={created_count}, Updated={updated_count}")
    return created_count, updated_count
