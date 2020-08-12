import pip


if __name__ == "__main__":
    try:
        from utils.server import main
    except ModuleNotFoundError as exc:
        print("看起来您好像没有安装必须的库.错误信息:")
        print(exc)
        exc = str(exc)
        exc = exc.split(" ")
        exc = exc[len(exc)-1]
        exc = exc.replace("'", "")
        print("缺少的库名字:", exc)
        print("正在尝试自动安装...")
        pip._internal.main(['install', 'websockets'])
        pip._internal.main(['install', 'requests'])
        print("安装完成！请重启程序.")
    except ImportError as exc:
        raise SystemExit("程序运行目录出错!请检查运行目录: \n", exc)
    except Exception as exc:
        print("未知错误: ", exc)
    else:
        main()