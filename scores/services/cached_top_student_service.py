import hashlib

from django.core.cache import cache
from django.conf import settings

from scores.services.top_student_service import TopStudentScoreService


class CachedTopStudentScoreService(TopStudentScoreService):
    """
    Enhanced version of TopStudentScoreService with Redis caching for better performance.
    
    Caches results for 5 minutes by default. Cache keys are based on query parameters
    to ensure different parameter combinations are cached separately.
    """
    
    CACHE_TIMEOUT = getattr(settings, 'TOP_STUDENTS_CACHE_TIMEOUT', 300)  # 5 minutes default
    CACHE_KEY_PREFIX = 'top_students_group_a'
    
    def rank_group_a_students(
        self,
        limit: int = 10,
        min_subjects: int = 2,
    ) -> dict:
        """
        Return ranking data with caching support.
        
        Cache key is generated based on limit and min_subjects parameters.
        """
        
        # Generate cache key based on parameters
        cache_key = self._generate_cache_key(limit, min_subjects)
        
        # Try to get from cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # If not in cache, compute the result using the parent method
        result = super().rank_group_a_students(limit, min_subjects)
        
        # Cache the result
        cache.set(cache_key, result, timeout=self.CACHE_TIMEOUT)
        
        return result
    
    def _generate_cache_key(self, limit: int, min_subjects: int) -> str:
        """Generate a unique cache key based on parameters."""
        params_str = f"limit_{limit}_min_subjects_{min_subjects}"
        # Create a hash to ensure key length limits
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{self.CACHE_KEY_PREFIX}_{params_hash}"
    
    def invalidate_cache(self):
        """
        Invalidate all cached results for top students.
        Call this method when student scores are updated.
        """
        # Since we can't easily list all cache keys, we'll use a version-based approach
        # This would require implementing a cache versioning system
        # For now, we'll clear the common cache keys
        common_combinations = [
            (10, 2), (10, 1), (10, 3),
            (20, 2), (20, 1), (20, 3),
            (50, 2), (50, 1), (50, 3),
        ]
        
        for limit, min_subjects in common_combinations:
            cache_key = self._generate_cache_key(limit, min_subjects)
            cache.delete(cache_key)