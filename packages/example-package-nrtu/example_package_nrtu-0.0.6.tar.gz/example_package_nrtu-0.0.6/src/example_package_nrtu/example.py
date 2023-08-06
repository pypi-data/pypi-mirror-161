import src_logger
import sys


def add_one(number):
    return number + 2


# プログラム入り口(直接実行用)
if __name__ == "__main__":
    src_logger.logger.info("Start")
    try:
        args = sys.argv
        add_one(number=int(args[1]))
    except Exception:
        src_logger.logger.exception("Exception")
        sys.exit(1)
    finally:
        src_logger.logger.info("End")
    sys.exit(0)
