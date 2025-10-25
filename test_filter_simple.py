"""简单测试脚本"""
import sys
sys.path.insert(0, '.')

from langlint.core.dispatcher import Dispatcher
from langlint.core.config import Config

# 创建配置和调度器
config = Config()
dispatcher = Dispatcher(config)

# 解析测试文件
test_file = "test_language_filter.py"
print(f"正在解析 {test_file}...")
result = dispatcher.parse_file(test_file)

print(f"\n文件: {test_file}")
print(f"找到 {len(result.parse_result.units)} 个可翻译单元\n")
print("="*100)

# 显示每个单元的详细信息
for i, unit in enumerate(result.parse_result.units, 1):
    content_preview = unit.content[:50] + "..." if len(unit.content) > 50 else unit.content
    print(f"\n#{i:2d} | 行 {unit.line_number:3d} | {unit.unit_type.value:15s} | {content_preview}")
    
print("\n" + "="*100)
print(f"\n总计: {len(result.parse_result.units)} 个可翻译单元")

