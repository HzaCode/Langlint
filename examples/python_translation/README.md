# Python Translation Example

This example demonstrates how to translate Python code comments and docstrings from different languages to English.

## Files

- `example_chinese.py` - Python file with Chinese comments and docstrings
- `example_japanese.py` - Python file with Japanese comments and docstrings

## Usage

### 1. Scan for translatable content

```bash
langlint scan example_chinese.py
```

**Output:**
```
Found 10 translatable units in example_chinese.py
- 5 docstrings
- 5 comments
```

### 2. Preview translation (dry-run)

```bash
langlint translate example_chinese.py -s zh-CN -t en --dry-run
```

### 3. Translate to new file

```bash
langlint translate example_chinese.py -s zh-CN -t en -o example_chinese_en.py
```

### 4. In-place translation with backup

```bash
langlint fix example_chinese.py -s zh-CN -t en
```

This creates:
- `example_chinese.py` - translated version
- `example_chinese.py.backup` - original backup

## Expected Results

### Before (Chinese)
```python
def calculate_sum(numbers):
    """
    计算数字列表的总和
    
    参数:
        numbers: 数字列表
    
    返回:
        总和
    """
    total = 0
    for num in numbers:
        # 累加每个数字
        total += num
    return total
```

### After (English)
```python
def calculate_sum(numbers):
    """
    Calculate the sum of a list of numbers
    
    Args:
        numbers: List of numbers
    
    Returns:
        Sum
    """
    total = 0
    for num in numbers:
        # Accumulate each number
        total += num
    return total
```

## Testing

Verify the translated code still works:

```bash
python example_chinese_en.py
# Should run without errors
```

## Notes

- Only comments and docstrings are translated
- Code structure and logic remain unchanged
- Original formatting and indentation are preserved

