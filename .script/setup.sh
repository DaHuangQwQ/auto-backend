echo "正在安装 uv 包管理器"
pip install uv

echo "正在安装 pre-commit 自动化测试工具"
pip install pre-commit

echo "正在同步包"
uv sync

echo "正在部署自动化测试"
export PRE_COMMIT_CONFIG=.script/.pre-commit-config.yaml
pre-commit install
