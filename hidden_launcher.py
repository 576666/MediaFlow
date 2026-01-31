import subprocess
import os
import sys
from pathlib import Path

def launch_mediaflow():
    """静默启动MediaFlow应用"""
    try:
        # 获取当前脚本所在目录
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # 使用subprocess启动主程序，隐藏控制台窗口
        if sys.platform.startswith('win'):
            # Windows平台下隐藏控制台窗口
            import ctypes
            from ctypes import wintypes
            
            # 尝试隐藏控制台
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # 获取当前进程信息
            h_stdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            
            # 使用subprocess启动应用，不显示控制台
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = 0  # SW_HIDE
            
            # 启动主程序
            process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                startupinfo=startup_info
            )
            
            print("MediaFlow已启动，请在新窗口中查看应用。")
            process.wait()
        else:
            # 非Windows平台
            subprocess.run([sys.executable, 'main.py'])
            
    except FileNotFoundError:
        print("错误：找不到Python解释器或main.py文件")
    except Exception as e:
        print(f"启动过程中发生错误: {e}")

if __name__ == "__main__":
    launch_mediaflow()