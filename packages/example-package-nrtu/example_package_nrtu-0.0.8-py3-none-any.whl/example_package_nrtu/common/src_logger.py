# -*- coding: UTF-8 -*-
# =================================
#  プログラム名: ログ用定数
#  プログラムID：src_logger.py
#  処理概要    ：機械学習ログ用定数管理ファイル
# =================================
import logging
import logging.handlers
import const
from logging import StreamHandler

# ================================
#  logging用定数
# ================================
# プログラム名
PG_NAME = "PG_NAME"
# Logファイルパス
path_LOG = const.FILE_PATH_LOG


# ================================
#  loggerの準備
# ================================
# Log記録用関数
def getLogger(pgname):
    # 全てのログを扱うストリームハンドラを生成
    sh = StreamHandler()

    handler = logging.handlers.RotatingFileHandler(
        path_LOG, maxBytes=1024 * 1024 * 1024, backupCount=10)
    fmt = "%(asctime)s - %(filename)s:%(lineno)s - %(message)s"
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger = logging.getLogger(pgname)

    logger.addHandler(sh)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


# Log出力用オブジェクト
logger = getLogger(PG_NAME)
