import sys
import subprocess
import time
import os
from pathlib import Path

def start_backend():
    """启动Flask后端服务器"""
    print("正在启动Flask后端服务器...")
    try:
        # 使用Popen启动后端进程
        backend_process = subprocess.Popen(
            [sys.executable, "simple_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Flask后端服务器启动成功！")
        return backend_process
    except Exception as e:
        print(f"启动后端服务器失败: {e}")
        return None

def start_frontend():
    """启动PyQt6前端应用"""
    print("正在启动PyQt6前端应用...")
    try:
        # 使用Popen启动前端进程
        frontend_process = subprocess.Popen(
            [sys.executable, "main_window.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("PyQt6前端应用启动成功！")
        return frontend_process
    except Exception as e:
        print(f"启动前端应用失败: {e}")
        return None

def main():
    print("=== 家庭食谱与膳食规划应用启动器 ===")
    print("正在检查环境...")
    
    # 检查必要的文件是否存在
    required_files = ["simple_app.py", "main_window.py"]
    for file in required_files:
        if not Path(file).exists():
            print(f"错误: 找不到文件 {file}")
            return
    
    print("所有必要文件已找到，开始启动应用...")
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        print("无法启动后端服务器，程序终止")
        return
    
    # 等待后端完全启动
    print("等待后端服务器初始化...")
    time.sleep(3)
    
    # 启动前端
    frontend_process = start_frontend()
    if not frontend_process:
        print("无法启动前端应用，关闭后端服务器...")
        backend_process.terminate()
        return
    
    print("\n应用已成功启动！")
    print("- Flask后端运行在: http://localhost:5000")
    print("- PyQt6前端应用界面已打开")
    print("\n按 Ctrl+C 可以停止所有服务")
    
    try:
        # 等待前端进程结束
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n正在关闭应用...")
    finally:
        # 关闭所有进程
        print("正在关闭后端服务器...")
        backend_process.terminate()
        backend_process.wait()
        print("应用已完全关闭")

if __name__ == "__main__":
    main()