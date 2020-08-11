import os
import sys
import threading
import pip


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MwebConsole.settings')
    try:
        from django.core.management import execute_from_command_line
    except:
        pip._internal.main(['install', 'django'])
        print("重要!Django未安装，现在已经自动安装。请重启程序!")
    execute_from_command_line(sys.argv)


def out():
    while True:
        sys.stdout.write('\r\n')


sys.stderr = sys.stdout
threading.Thread(target=out, daemon=True).start()
main()
