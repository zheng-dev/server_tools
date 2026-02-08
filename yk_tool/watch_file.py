#
# coding=utf-8
# py3.12.5
# Auther:zhengzhichun [zheng6655@163.com]
# Date: 2026-01-09
# decription: 文件目录变动监听
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileCreateHandler(FileSystemEventHandler):
    """自定义事件处理器，只处理创建事件"""

    def on_created(self, event):
        if event.is_directory:
            print(f"[目录创建] {event.src_path}")
        else:
            print(f"[文件创建] {event.src_path}")

    def on_deleted(self, event):
        print(f"[del操作] {event.src_path}")


def main():
    event_handler = FileCreateHandler()
    observer = Observer()
    list1 = [
        f"c:/",
        f"d:/",
        f"e:/",
        f"f:/",
        f"g:/",
        #  f"i:/"
    ]
    for i in list1:
        observer.schedule(event_handler, i, recursive=True)

    # 启动监控
    observer.start()
    print(f"开始监控目录:  (按 Ctrl+C 停止)", list1)

    try:
        while True:
            time.sleep(1)  # 保持主线程运行
    except KeyboardInterrupt:
        observer.stop()
        print("\n监控已停止")

    observer.join()


if __name__ == "__main__":
    main()
