import traceback

if __name__ == "__main__":
    try:
        try:
            from utils.server import main
        except ImportError:
            traceback.print_exc()
            from mwclibs.utils.server import main
    except:
        print("看起来您好像没有安装必须的库: ")
        traceback.print_exc()
    else:
        main()