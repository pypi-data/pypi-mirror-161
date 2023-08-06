import src_logger
def add_one(number):
    src_logger.logger.info("Start")
    try:
        return number + 2
    except Exception:
        src_logger.logger.exception("Exception")
    finally:
        src_logger.logger.info("End")