# ============================================================================
# CLEAN SCRIPT - Xóa các file cache và temporary
# ============================================================================

# Hướng dẫn sử dụng:
# PowerShell: .\clean.ps1
# Bash/Linux: chmod +x clean.sh && ./clean.sh

# ============================================================================
# XÓA PYTHON CACHE
# ============================================================================

# Xóa tất cả __pycache__ directories
# PowerShell:
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Linux/Mac:
# find . -type d -name "__pycache__" -exec rm -rf {} +

# ============================================================================
# XÓA .PYC FILES
# ============================================================================

# Xóa tất cả .pyc, .pyo files
# PowerShell:
Get-ChildItem -Path . -Recurse -Include "*.pyc","*.pyo" | Remove-Item -Force

# Linux/Mac:
# find . -type f -name "*.pyc" -delete
# find . -type f -name "*.pyo" -delete

# ============================================================================
# XÓA COVERAGE DATA
# ============================================================================

# PowerShell:
Get-ChildItem -Path . -Recurse -Include ".coverage","coverage.xml",".pytest_cache" | Remove-Item -Recurse -Force

# ============================================================================
# XÓA BUILD ARTIFACTS
# ============================================================================

# PowerShell:
Get-ChildItem -Path . -Recurse -Include "*.egg-info","build","dist" | Remove-Item -Recurse -Force

# ============================================================================
# XÓA IDE SETTINGS (Optional)
# ============================================================================

# PowerShell:
Get-ChildItem -Path . -Recurse -Include ".vscode",".idea","*.swp" | Remove-Item -Recurse -Force

# ============================================================================
# QUICK CLEAN COMMANDS
# ============================================================================

# PowerShell - Xóa tất cả cache (chạy từ root project):
# Get-ChildItem -Recurse -Include __pycache__,*.pyc,*.pyo,.pytest_cache,.coverage | Remove-Item -Recurse -Force

# Linux/Mac - Xóa tất cả cache:
# find . -type d -name "__pycache__" -exec rm -rf {} + ; find . -type f -name "*.pyc" -delete

# ============================================================================
# SAU KHI CLEAN
# ============================================================================

# Kiểm tra git status:
# git status

# Xem những file bị ignore:
# git status --ignored

# Test .gitignore:
# git check-ignore -v <filename>
