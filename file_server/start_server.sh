#!/bin/sh

dir=$(cd "$(dirname "$0")" && pwd)

python_script="${dir}/main_app.py"

if [ ! -f "${python_script}" ]; then
    echo "错误：找不到脚本文件 ${python_script}"
    exit 1
fi

nohup /usr/bin/python3 "${python_script}" > "${dir}/logs/start.log" 2>&1 &

echo "服务已后台启动！"
echo "进程ID：$!"