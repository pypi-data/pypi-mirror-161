import src_logger
import sys


def add_one(number):
    src_logger.logger.info("Start")
    try:
        return number + 2
    except Exception:
        src_logger.logger.exception("Exception")
    finally:
        src_logger.logger.info("End")


# プログラム入り口(直接実行用)
if __name__ == "__main__":
    src_logger.logger.info("Start")
    try:
        args = sys.argv
        a = add_one(number=int(args[1]))
        print(a)
    except Exception:
        src_logger.logger.exception("Exception")
        sys.exit(1)
    finally:
        src_logger.logger.info("End")
    sys.exit(0)
