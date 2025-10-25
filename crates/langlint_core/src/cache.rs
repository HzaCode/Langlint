use crate::types::ParseResult;
use dashmap::DashMap;
use std::sync::Arc;

/// Thread-safe cache for parse results
///
/// This cache uses content hashing to store and retrieve parse results,
/// avoiding redundant parsing of unchanged files.
pub struct Cache {
    inner: Arc<DashMap<String, ParseResult>>,
}

impl Cache {
    /// Create a new empty cache
    pub fn new() -> Self {
        Self {
            inner: Arc::new(DashMap::new()),
        }
    }

    /// Get a parse result from the cache
    pub fn get(&self, key: &str) -> Option<ParseResult> {
        self.inner.get(key).map(|entry| entry.clone())
    }

    /// Store a parse result in the cache
    pub fn set(&self, key: String, value: ParseResult) {
        self.inner.insert(key, value);
    }

    /// Check if a key exists in the cache
    pub fn contains_key(&self, key: &str) -> bool {
        self.inner.contains_key(key)
    }

    /// Remove an entry from the cache
    pub fn remove(&self, key: &str) -> Option<ParseResult> {
        self.inner.remove(key).map(|(_, v)| v)
    }

    /// Clear all entries from the cache
    pub fn clear(&self) {
        self.inner.clear();
    }

    /// Get the number of entries in the cache
    pub fn len(&self) -> usize {
        self.inner.len()
    }

    /// Check if the cache is empty
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Generate a cache key from file path and content
    pub fn generate_key(file_path: &str, content: &str) -> String {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        file_path.hash(&mut hasher);
        content.hash(&mut hasher);
        format!("{}:{:x}", file_path, hasher.finish())
    }
}

impl Default for Cache {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{TranslatableUnit, UnitType};

    fn create_test_result() -> ParseResult {
        let unit = TranslatableUnit::new("test content".to_string(), UnitType::Comment, 1, 0);

        ParseResult::new("python", "utf-8", 10).with_units(vec![unit])
    }

    #[test]
    fn test_cache_new() {
        let cache = Cache::new();
        assert_eq!(cache.len(), 0);
        assert!(cache.is_empty());
    }

    #[test]
    fn test_cache_set_and_get() {
        let cache = Cache::new();
        let result = create_test_result();

        cache.set("test_key".to_string(), result.clone());

        assert_eq!(cache.len(), 1);
        assert!(!cache.is_empty());

        let retrieved = cache.get("test_key");
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().file_type, "python");
    }

    #[test]
    fn test_cache_contains_key() {
        let cache = Cache::new();
        let result = create_test_result();

        assert!(!cache.contains_key("test_key"));

        cache.set("test_key".to_string(), result);

        assert!(cache.contains_key("test_key"));
    }

    #[test]
    fn test_cache_remove() {
        let cache = Cache::new();
        let result = create_test_result();

        cache.set("test_key".to_string(), result);
        assert_eq!(cache.len(), 1);

        let removed = cache.remove("test_key");
        assert!(removed.is_some());
        assert_eq!(cache.len(), 0);
        assert!(!cache.contains_key("test_key"));
    }

    #[test]
    fn test_cache_clear() {
        let cache = Cache::new();

        cache.set("key1".to_string(), create_test_result());
        cache.set("key2".to_string(), create_test_result());
        cache.set("key3".to_string(), create_test_result());

        assert_eq!(cache.len(), 3);

        cache.clear();

        assert_eq!(cache.len(), 0);
        assert!(cache.is_empty());
    }

    #[test]
    fn test_cache_generate_key() {
        let key1 = Cache::generate_key("test.py", "content1");
        let key2 = Cache::generate_key("test.py", "content1");
        let key3 = Cache::generate_key("test.py", "content2");
        let key4 = Cache::generate_key("other.py", "content1");

        // Same inputs should generate same key
        assert_eq!(key1, key2);

        // Different content should generate different key
        assert_ne!(key1, key3);

        // Different path should generate different key
        assert_ne!(key1, key4);
    }

    #[test]
    fn test_cache_multiple_entries() {
        let cache = Cache::new();

        for i in 0..10 {
            cache.set(format!("key{}", i), create_test_result());
        }

        assert_eq!(cache.len(), 10);

        for i in 0..10 {
            assert!(cache.contains_key(&format!("key{}", i)));
        }
    }

    #[test]
    fn test_cache_overwrite() {
        let cache = Cache::new();

        cache.set("key".to_string(), create_test_result());
        assert_eq!(cache.len(), 1);

        // Overwrite with new value
        cache.set("key".to_string(), create_test_result());
        assert_eq!(cache.len(), 1); // Still only 1 entry
    }

    #[test]
    fn test_cache_default() {
        let cache = Cache::default();
        assert_eq!(cache.len(), 0);
        assert!(cache.is_empty());
    }
}
