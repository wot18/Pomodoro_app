#!/bin/bash

echo "==========================================="
echo "番茄钟 - Pomodoro Timer"
echo "==========================================="
echo ""

# 激活已存在的虚拟环境
conda activate gptac_venv

if [ $? -ne 0 ]; then
    echo "错误: 无法激活虚拟环境 'gptac_venv'"
    echo "请检查conda是否安装正确"
    exit 1
fi

# 运行程序
echo "启动番茄钟..."
python main.py

if [ $? -ne 0 ]; then
    echo "程序运行出错，请查看上方错误信息"
fi
