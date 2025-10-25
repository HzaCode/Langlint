# Jupyter Notebook Translation Example

This example demonstrates how to translate Jupyter notebooks with multilingual markdown cells and code comments.

## Files

- `data_analysis.ipynb` - Jupyter notebook with Chinese markdown and comments

## Usage

### 1. Scan the notebook

```bash
langlint scan data_analysis.ipynb
```

### 2. Translate the notebook

```bash
langlint translate data_analysis.ipynb -s zh-CN -t en -o data_analysis_en.ipynb
```

### 3. View the translated notebook

```bash
jupyter notebook data_analysis_en.ipynb
```

## What Gets Translated

✅ **Translated:**
- Markdown cell content
- Code comments (`# 导入必要的库`)
- Docstrings in code cells

❌ **Not Translated:**
- Python code (variable names, function names)
- String literals in code
- Cell outputs

## Expected Results

### Before (Chinese)

**Markdown cell:**
```markdown
# 数据分析示例

这个笔记本演示了基本的数据分析流程
```

**Code cell:**
```python
# 导入必要的库
import pandas as pd
import numpy as np
```

### After (English)

**Markdown cell:**
```markdown
# Data Analysis Example

This notebook demonstrates a basic data analysis workflow
```

**Code cell:**
```python
# Import necessary libraries
import pandas as pd
import numpy as np
```

## Notes

- Notebook structure (cell order, cell types) is preserved
- Code execution results are not affected
- Notebook metadata remains unchanged
- Original notebook can be backed up automatically

