import unittest
from cache import get_from_cache, put_in_cache, cache_max_size
from cache import put_in_cache


class TestCacheFunctions(unittest.TestCase):

    def test_get_from_cache_existing_key(self):
        key = "existing_key"
        value = "existing_value"
        put_in_cache(key, value)
        result = get_from_cache(key)
        self.assertEqual(result, value)

    def test_get_from_cache_non_existing_key(self):
        key = "non_existing_key"
        result = get_from_cache(key)
        self.assertIsNone(result)

    def test_put_in_cache_within_capacity(self):
        key = "new_key"
        value = "new_value"
        put_in_cache(key, value)
        result = get_from_cache(key)
        self.assertEqual(result, value)

    def test_put_in_cache_exceeding_capacity(self):
        for i in range(2*cache_max_size):
            put_in_cache(f'new_key{i}', f'new_value{1}')

        result = get_from_cache('existing_key')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
