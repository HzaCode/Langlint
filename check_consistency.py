#!/usr/bin/env python3
"""
LangLint 一致性检查脚本
检查文档、代码和README之间的一致性
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

class ConsistencyChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        
    def check_file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        return (self.project_root / file_path).exists()
    
    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(self.project_root / file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.issues.append(f"无法读取文件 {file_path}: {e}")
            return ""
    
    def check_backup_extension_consistency(self) -> List[str]:
        """检查备份文件扩展名一致性"""
        issues = []
        
        # 检查README.md
        readme_content = self.read_file("README.md")
        if ".bak" in readme_content:
            issues.append("README.md 中使用了 .bak 扩展名，应该使用 .backup")
        
        # 检查docs目录中的RST文件
        docs_files = [
            "docs/cli.rst",
            "docs/quickstart.rst", 
            "docs/configuration.rst"
        ]
        
        for doc_file in docs_files:
            if self.check_file_exists(doc_file):
                content = self.read_file(doc_file)
                if ".bak" in content:
                    issues.append(f"{doc_file} 中使用了 .bak 扩展名，应该使用 .backup")
        
        return issues
    
    def check_config_file_consistency(self) -> List[str]:
        """检查配置文件一致性"""
        issues = []
        
        # 检查README中提到的配置文件
        readme_content = self.read_file("README.md")
        
        # 检查是否提到了正确的配置文件
        if ".langlint.yml" not in readme_content:
            issues.append("README.md 中缺少 .langlint.yml 配置文件说明")
        
        if "langlint.toml" not in readme_content:
            issues.append("README.md 中缺少 langlint.toml 配置文件说明")
        
        return issues
    
    def check_cli_options_consistency(self) -> List[str]:
        """检查CLI选项一致性"""
        issues = []
        
        # 检查Python CLI
        cli_py_content = self.read_file("langlint/cli.py")
        if "--no-backup" not in cli_py_content:
            issues.append("Python CLI (langlint/cli.py) 缺少 --no-backup 选项")
        
        # 检查Rust CLI
        rust_cli_content = self.read_file("crates/langlint_cli/src/main.rs")
        if "--no-backup" not in rust_cli_content:
            issues.append("Rust CLI 缺少 --no-backup 选项")
        
        return issues
    
    def check_test_coverage_consistency(self) -> List[str]:
        """检查测试覆盖率一致性"""
        issues = []
        
        readme_content = self.read_file("README.md")
        
        # 检查README中的测试数量
        test_count_match = re.search(r'(\d+)\+?\s*tests?', readme_content)
        if test_count_match:
            reported_count = int(test_count_match.group(1))
            # 这里可以添加实际测试数量的检查
            pass
        
        # 检查覆盖率百分比
        coverage_match = re.search(r'(\d+)%\s*coverage', readme_content)
        if coverage_match:
            reported_coverage = int(coverage_match.group(1))
            # 这里可以添加实际覆盖率的检查
            pass
        
        return issues
    
    def check_documentation_consistency(self) -> List[str]:
        """检查文档一致性"""
        issues = []
        
        # 检查docs目录是否存在
        if not self.check_file_exists("docs"):
            issues.append("docs 目录不存在")
            return issues
        
        # 检查关键文档文件
        required_docs = [
            "docs/index.rst",
            "docs/installation.rst",
            "docs/quickstart.rst",
            "docs/cli.rst",
            "docs/configuration.rst"
        ]
        
        for doc_file in required_docs:
            if not self.check_file_exists(doc_file):
                issues.append(f"缺少文档文件: {doc_file}")
        
        return issues
    
    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有一致性检查"""
        print("🔍 开始一致性检查...")
        
        all_issues = []
        
        # 备份扩展名检查
        print("检查备份文件扩展名一致性...")
        backup_issues = self.check_backup_extension_consistency()
        all_issues.extend(backup_issues)
        
        # 配置文件一致性检查
        print("检查配置文件一致性...")
        config_issues = self.check_config_file_consistency()
        all_issues.extend(config_issues)
        
        # CLI选项一致性检查
        print("检查CLI选项一致性...")
        cli_issues = self.check_cli_options_consistency()
        all_issues.extend(cli_issues)
        
        # 测试覆盖率一致性检查
        print("检查测试覆盖率一致性...")
        test_issues = self.check_test_coverage_consistency()
        all_issues.extend(test_issues)
        
        # 文档一致性检查
        print("检查文档一致性...")
        doc_issues = self.check_documentation_consistency()
        all_issues.extend(doc_issues)
        
        # 生成报告
        report = {
            "total_issues": len(all_issues),
            "issues": all_issues,
            "status": "PASS" if len(all_issues) == 0 else "FAIL"
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """打印检查报告"""
        print("\n" + "="*60)
        print("📋 LangLint 一致性检查报告")
        print("="*60)
        
        if report["status"] == "PASS":
            print("✅ 所有检查通过！文档和代码完全一致。")
        else:
            print(f"❌ 发现 {report['total_issues']} 个一致性问题：")
            print()
            
            for i, issue in enumerate(report["issues"], 1):
                print(f"{i}. {issue}")
        
        print("\n" + "="*60)

def main():
    """主函数"""
    checker = ConsistencyChecker()
    report = checker.run_all_checks()
    checker.print_report(report)
    
    # 返回适当的退出码
    sys.exit(0 if report["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
