#!/usr/bin/env python3

import logging

def logToFile(message):
    # 设置日志文件的路径
    log_file = 'log.txt'
    # 设置基本配置
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,  # 设置日志级别为 INFO
        format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
        datefmt='%Y-%m-%d %H:%M:%S'  # 设置日期格式
    )
    # 记录一条日志信息
    logging.info(message)

# 主函数
def main():
    #---初始化数据---
    logToFile("程序初始化完成")

# 调用主函数
if __name__ == "__main__":
    main()
