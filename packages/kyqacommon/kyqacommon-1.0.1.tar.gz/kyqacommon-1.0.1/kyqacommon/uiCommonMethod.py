import os
import time
from contextlib import redirect_stdout
from functools import wraps

import pyautogui

casedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
timeStr = time.strftime("%m%d_%H_%M_%S")


def printfiers(func):
    @wraps(func)
    def __wrapper(*args,**arges):
        anydlg ,filePath,fileName = func(*args,**arges)
        '''
        :param anydlg: dlg
        :param filePath: 文件路径
        :param fileName: 文件名称
        '''
        action = "anydlg.print_control_identifiers()"
        identifiersPath = os.path.join(filePath, "identifiersFile",
                                       "identifiers{}_{}.txt".format(timeStr, fileName))
        with open(identifiersPath, "w", encoding="utf8") as f:
            with redirect_stdout(f):
                eval(action)
    return __wrapper

@printfiers
def printidentifiers(anydlg,filePath,fileName = "dlg"):
    '''
    :param anydlg: dlg
    :param filePath: 文件路径
    :param fileName: 文件名称,非必填项
    :return:调用此方法，可以打印出控件信息并保存到文件中，保存路径和文件名称可自定义；
    '''
    return anydlg,filePath,fileName



class CommonMethod():
    @staticmethod
    def pointLocateOnScreen(img_file):
        '''
        :param img_file: 图片路径
        :return: 通过图片识别的控件 中心点坐标
        '''
        img_point = pyautogui.locateCenterOnScreen(img_file, grayscale=False)
        i = 1
        while True:
            i = i - 0.1
            if not img_point:
                img_point = pyautogui.locateCenterOnScreen(img_file, grayscale=False, confidence=i)
            else:
                info = "控件截图识别成功point:{}最后识别精度为{}".format(img_point, i)
                return img_point
            if i < 0.5:
                fail = "控件截图未识别成功,最后识别精度为{}".format(i)
                print(fail)
                break

