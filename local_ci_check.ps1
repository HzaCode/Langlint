# 本地复现 CI 检查的脚本

Write-Host "=== 运行和 CI 相同的检查 ===" -ForegroundColor Cyan

# 1. 运行测试（排除 langlint_py）
Write-Host "`n[1/3] 运行测试..." -ForegroundColor Yellow
cargo test --workspace --verbose --exclude langlint_py
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 测试失败" -ForegroundColor Red
    exit 1
}

# 2. 运行 Clippy（把警告当错误）
Write-Host "`n[2/3] 运行 Clippy..." -ForegroundColor Yellow
cargo clippy --all-targets --all-features --workspace --exclude langlint_py -- -D warnings
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Clippy 检查失败" -ForegroundColor Red
    exit 1
}

# 3. 检查代码格式
Write-Host "`n[3/3] 检查格式..." -ForegroundColor Yellow
cargo fmt -- --check
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 格式检查失败，运行 'cargo fmt' 修复" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== ✓ 所有检查通过！ ===" -ForegroundColor Green

