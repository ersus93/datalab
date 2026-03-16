"""Utilitario de caché para DataLab usando Redis."""
import json
import logging
from functools import wraps
from typing import Any, Callable, Optional

import redis

logger = logging.getLogger(__name__)

CACHE_TTL_DEFAULT = 300


class CacheManager:
    """Gestor de caché con Redis."""

    _instance: Optional['CacheManager'] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def init_app(self, app) -> None:
        """Inicializar Redis con configuración de la app."""
        redis_url = app.config.get('REDIS_URL')
        if redis_url:
            try:
                self._client = redis.from_url(
                    redis_url,
                    decode_responses=True
                )
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis not available: {e}. Using no-op cache.")
                self._client = None
        else:
            logger.warning("REDIS_URL not configured. Cache disabled.")
            self._client = None

    def get(self, key: str) -> Optional[Any]:
        """Obtener valor de caché."""
        if not self._client:
            return None
        try:
            value = self._client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = CACHE_TTL_DEFAULT) -> bool:
        """Establecer valor en caché."""
        if not self._client:
            return False
        try:
            serialized = json.dumps(value)
            self._client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Eliminar valor de caché."""
        if not self._client:
            return False
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Limpiar todas las claves que coincidan con el patrón."""
        if not self._client:
            return 0
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
        return 0


cache = CacheManager()


def cached(key_prefix: str, ttl: int = CACHE_TTL_DEFAULT):
    """Decorador para caching de funciones.

    Args:
        key_prefix: Prefijo para la clave de caché
        ttl: Time-to-live en segundos (default 5 minutos)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import current_app

            cache_key = f"{key_prefix}:{':'.join(str(a) for a in args)}"

            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)

            cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> int:
    """Invalidar caché por patrón."""
    return cache.clear_pattern(pattern)
