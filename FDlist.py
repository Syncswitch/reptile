#!/usr/bin/env python3

import requests,csv,os,logging

# 输出日志到文件
def logToFile(message):
    # 设置日志文件的路径
    log_file = 'FDlist.log'
    # 设置基本配置
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,  # 设置日志级别为 INFO
        format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
        datefmt='%Y-%m-%d %H:%M:%S'  # 设置日期格式
    )
    # 记录一条日志信息
    logging.info(message)

# 请求网页源码
def fetchPage(url, method="get", data=None, headers=None):
    # 默认 User-Agent
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 合并用户自定义 headers 和默认 headers
    if headers:
        default_headers.update(headers)
    headers = default_headers
    
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers, timeout=10, params=data)
        elif method.lower() == "post":
            response = requests.post(url, headers=headers, timeout=10, data=data)
        else:
            #print("请求方法不支持，仅支持 'get' 或 'post'")
            return None
        
        # 检查请求是否成功
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        #print("请求超时")
        return None
    except requests.exceptions.RequestException as e:
        #print(f"请求失败: {e}")
        return None

# 取文本中间内容
def extractMid(text, start, end):
    try:
        # 如果 start 为空，从文本开头开始
        startIndex = 0 if not start else text.index(start) + len(start)
        # 如果 end 为空，直接取到文本末尾
        endIndex = len(text) if not end else text.index(end, startIndex)
        return text[startIndex:endIndex]
    except ValueError:
        return None

# 获取基金数据
def getFundData(code):
    #---组装http请求所需要的数据---
    # 根据参数提供的基金代码生成url
    url = 'http://fund.eastmoney.com/pingzhongdata/' + code + '.js'
    # 生成headers
    headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": ""
    }
    # 根据基金代码更新headers
    headers['Referer'] = 'http://fund.eastmoney.com/' + code + '.html'
    #print(headers)
    #---请求api接口获取原始数据---
    html = fetchPage(url, method="get", headers=headers)
    if not html:
        # 请求失败
        #print('请求HTML失败！')
        return None
    html2 = extractMid(html,'var Data_netWorthTrend = ','var Data_ACWorthTrend =') 
    temp = html2.split('},{')
    if len(temp) > 0:
        html2 = temp[len(temp)-1]
    #print(html2)
    fd = {}
    fd['code'] = extractMid(html,'fS_code = "','";/*原费率*/') # 截取基金代码
    fd['name'] = extractMid(html,'fS_name = "','";var fS_code') # 截取基金名称
    fd['y'] = extractMid(html2,',"y":',',"equityReturn') # 截取最新净值数据
    fd['e'] = extractMid(html2,'Return":',',"unitMoney') # 截取最新涨跌幅数据
    fd['sy_1y'] = extractMid(html,'var syl_1y="','";/*股票仓位测算图*') # 截取近一个月收益数据
    fd['sy_3y'] = extractMid(html,'var syl_3y="','";/*近一月收益率*/') # 截取近三个月收益数据
    fd['sy_6y'] = extractMid(html,'var syl_6y="','";/*近三月收益率*/') # 截取近六个月收益数据
    fd['sy_1n'] = extractMid(html,'var syl_1n="','";/*近6月收益率*/') # 截取近一年收益数据
    html2 = extractMid(html,'/*现任基金经理*/','/*申购赎回*/')
    fd['date'] = extractMid(html,']}],"jzrq":"','"').replace('-', '') # 截取
    #print(fd)
    if (
        fd['code'] is None
        or fd['name'] is None
        or fd['y'] is None 
        or fd['e'] is None
        or fd['date'] is None
    ):
        return None
    else:
        return fd

# 保存基金数据到csv文件
def saveToCsv(data):
    #---初始化变量---
    filename = f"{data['code']}.csv" # 生成文件名
    headers = ['代码', '名称', '净值', '涨跌', '近1月', '近3月', '近6月', '近1年', '日期'] # 生成csv表头
    # headers = ['code', 'name', 'y', 'e', 'sy_1y', 'sy_3y', 'sy_6y', 'sy_1n', 'date'] # 生成csv表头
    date_exists = False # 初始化写入开关
    file_exists = os.path.isfile(filename) # 判断文件是否存在
    # 建立英文键与中文表头的映射关系
    header_map = {
        '代码': 'code',
        '名称': 'name',
        '净值': 'y',
        '涨跌': 'e',
        '近1月': 'sy_1y',
        '近3月': 'sy_3y',
        '近6月': 'sy_6y',
        '近1年': 'sy_1n',
        '日期': 'date'
    }
    #---检查文件是否存在并读取文件内容---
    if file_exists:
        # 如果csv文件从在
        with open(filename, mode='r', newline='', encoding='utf-8') as file: # 打开文件
            reader = csv.DictReader(file) # 读取csv文件数据
            # 循环读取每一行数据
            for row in reader:
                if row.get('日期') == data['date']: # 数据已存在
                    date_exists = True # 跳过写入
                    break
    
    # 如果 date 值已存在则跳过写入
    if date_exists:
        logToFile(f"{data['name']} 日期为：{data['date']} 的数据已存在于 {filename} 中，跳过写入。") # 打印日志
        print(f"{data['name']} 日期为：{data['date']} 的数据已存在于 {filename} 中，跳过写入。")
        return

    # 写入文件，如果文件不存在则添加表头
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists: #如果csv文件不存在
            print('csv文件不存在')
            writer.writerow(headers) # 写入表头
        # 按表头顺序写入数据，缺少的字段填入空字符串
        # writer.writerow([data.get(header, '') for header in headers])
        writer.writerow([data.get(header_map.get(header, ''), '') for header in headers])
    # 记录日志
    logToFile(f"{data['name']} 日期为：{data['date']} 的数据已成功追加到 {filename}")
    print(f"{data['name']} 日期为：{data['date']} 的数据已成功追加到 {filename}")

# 主函数
def main():
    file_exists = os.path.isfile('FDlist.csv') # 判断文件是否存在
    if file_exists:
        # 如果csv文件从在
        with open('FDlist.csv', mode='r', newline='', encoding='utf-8') as file: # 打开文件
            reader = csv.DictReader(file) # 读取csv文件数据
            # 循环读取每一行数据
            for row in reader:
                logToFile(f"正在抓取：({row.get('代码')}){row.get('名称')} 数据...") # 打印日志
                print(f"正在抓取：({row.get('代码')}){row.get('名称')} 数据...")
                fd = getFundData(row.get('代码'))
                if fd is None:
                    # 抓取失败
                    logToFile(f"抓取：({row.get('代码')}){row.get('名称')} 数据失败") # 打印日志
                    print(f"抓取：({row.get('代码')}){row.get('名称')} 数据失败")
                    print(fd)
                else:
                    # 抓取成功
                    logToFile(f"抓取：({row.get('代码')}){row.get('名称')} 数据成功") # 打印日志
                    print(f"抓取：({row.get('代码')}){row.get('名称')} 数据成功")
                    fd['name'] = row.get('名称')
                    saveToCsv(fd)

# 调用主函数
if __name__ == "__main__":
    main()
