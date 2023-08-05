import os
import sys
import time

r=os.path.abspath(os.path.dirname(__file__))
rootpath=os.path.split(r)[0]
sys.path.append(os.path.split(r)[0])
import logging
from logging import handlers


def handle_log(log_path):
    '''

    :param log_path: 必须定义日志文件需要保存的位置；
    :return:
    '''
    log_file_name = time.strftime("%Y%m%d", time.localtime())
    log_dir = os.path.join(log_path,'{}_kyuiAutoTest.log'.format(log_file_name))
    kyAAT = logging.getLogger(name='kyAAT')

    pycharm = logging.StreamHandler()#控制台渠道
    with open(log_dir, "w+") as f:
        pass
    file = handlers.TimedRotatingFileHandler( filename=log_dir, when='D', encoding='utf-8',interval=1, backupCount=10)

    #日志格式
    fmt = '\033[35m%(asctime)s-%(name)s-%(levelname)s-%(filename)s-%(funcName)s-[line:%(lineno)d]：%(message)s\033[0m'
    log_fmt = logging.Formatter(fmt=fmt)

    kyAAT.setLevel(logging.DEBUG)

    pycharm.setFormatter(fmt=log_fmt)
    file.setFormatter(fmt=log_fmt)

    #渠道
    kyAAT.addHandler(pycharm)
    kyAAT.addHandler(file)
    return kyAAT
