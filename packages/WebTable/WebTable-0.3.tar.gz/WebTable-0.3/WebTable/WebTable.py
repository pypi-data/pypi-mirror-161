import os
import time

import pandas as pd
import re
import requests
from opencc import OpenCC
import openpyxl
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio
import pyppeteer
from bs4 import BeautifulSoup

logging.captureWarnings(True)  # 去掉建议使用SSL验证的显示


def exist():
    file_list = ['_'.join(item.split('.')[0].split('_')[:-1]) for item in os.listdir('data')]
    file_set = set()
    for item in set(file_list):
        if file_list.count(item) <= 3:
            file_set.add(item)
    return file_set


def crawler_html(url):
    html = requests.get(url=url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/72.0.3626.119 Safari/537.36'}, verify=False)
    html = html.content.decode('utf-8', 'ignore')
    return html


def read_list_names():
    data = []
    file = open('zhwiki-latest-pages-articles-multistream-index.txt')
    for line in file:
        query = line.strip().split(':')[-1]
        if '列表' in query:
            data.append(query)
    print('before: {}'.format(len(data)))

    exist_queries = exist()
    data = list(set(data) - exist_queries)
    print('after: {}'.format(len(data)))
    return data


def clean(df):
    columns = list(df.columns)
    if '备注' in set(columns):
        df = df.drop(columns=['备注'])
    for col in columns:
        if 'Unnamed' in col:
            df = df.rename(columns={col: ''})
        elif isinstance(col, tuple):
            length = len(col)
            df = df.drop(index=list(range(length - 1)))
            break
        elif '[' in col:
            new_col = re.sub('\[.+\]', '', col)
            df = df.rename(columns={col: new_col})
        elif len(col) > 100:
            df = df.rename(columns={col: col.split('.')[0]})
    return df


def crawler():
    query_pool = read_list_names()
    for query in query_pool:
        url = 'http://zh.wikipedia.org/wiki/' + query
        print(url)
        html = crawler_html(url)
        try:
            html_data = pd.read_html(html, attrs={'class': 'wikitable'})
        except:
            continue

        for i, item in enumerate(html_data):
            table_data = pd.DataFrame(item)
            try:
                table_data = clean(table_data)
            except:
                pass
            table_data.to_csv('tables/{}_{}.csv'.format(query.replace('/', '_'), i), index=False)


def tradition_to_simple(df):
    if df is None or df.empty:
        return None
    cc = OpenCC('t2s')
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            df.iat[i, j] = cc.convert(str(df.iat[i, j]))
    new_df_columns = []
    for item in df.columns:
        new_df_columns.append(cc.convert(str(item)))
    df.columns = new_df_columns
    return df


def remove_upprintable_chars(s):
    """移除所有不可见字符"""
    return ''.join(x for x in s if x.isprintable())


# 去除大括号、中括号、小括号、尖括号中的内容
# 注意：因为muti_index_process()函数中会生成小括号，本函数必须在其前面运行！
def brackets_remove(df):
    if df is None or df.empty:
        return None
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            df.iat[i, j] = remove_upprintable_chars(re.sub(u"{.*?}|\\[.*?]|<.*?>", "", str(df.iat[i, j])))
            # 这里我们认为-的效果和没有是一样的，并且去掉？和nan
            df.iat[i, j] = df.iat[i, j].replace('？', '').replace('nan', '')
            if df.iat[i, j] == '' or df.iat[i, j] == '－':
                df.iat[i, j] = None

    new_df_columns = []
    for item in df.columns:
        new_df_columns.append(re.sub(u"{.*?}|\\[.*?]|<.*?>", "", str(item)))
    df = df[new_df_columns]
    return df


def empty_column_remove(df, max_empty_percentage: float, if_strict=False):
    if df is None or df.empty:
        return None
    try:
        # 删除有效内容过少的列
        delete_index_list = []
        for df_index, row in df.iteritems():
            if float(sum(row.isnull() == True)) / (0.01 + df.shape[0]) > max_empty_percentage:
                delete_index_list.append(df_index)
        df.drop(delete_index_list, axis=1, inplace=True)

        # 删除有效内容过少的行
        delete_index_list = []
        for df_index, row in df.iterrows():
            if float(sum(row.isnull() == True)) / (0.01 + df.shape[1]) > max_empty_percentage:
                delete_index_list.append(df_index)
        df.drop(delete_index_list, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # 删除索引是数字或是与其他列相同的列
        delete_index_list = []
        for df_index, row in df.iteritems():
            if str(df_index).isdigit() or 'Unnamed' in str(df_index) \
                    or '参考' in str(df_index) or '来源' in str(df_index) or '#' in str(df_index):
                delete_index_list.append(df_index)
        df.drop(delete_index_list, axis=1, inplace=True)

        # 删除一行内容都相同的行
        delete_index_list = []
        for df_index, row in df.iterrows():
            flag = True
            for i in range(df.shape[1] - 1):
                if row[i] != row[i + 1]:
                    flag = False
                    break
            if flag:
                delete_index_list.append(df_index)
        df.drop(delete_index_list, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # 删除一列内容都相同的列
        if df.shape[0] >= 3:
            delete_index_list = []
            for df_index, row in df.iteritems():
                flag = True
                for i in range(df.shape[0] - 1):
                    if row[i] != row[i + 1]:
                        flag = False
                        break
                if flag:
                    delete_index_list.append(df_index)
            df.drop(delete_index_list, axis=1, inplace=True)

        if df.empty or df.shape[1] == 1 or df.shape[0] <= 2:
            if if_strict:
                return None
            else:
                return df
        else:
            return df
    except Exception as e:
        print(e)
        return None


# 判断重复表头，并将两个重复的表头合并
def muti_index_process(df, if_strict=False):
    if df is None or df.empty:
        return None
    flag = False
    for i in range(df.shape[1]):
        if str(df.iloc[[0], [i]].values[0][0]) == str(df.columns[i]):
            flag = True
            break
    if flag:
        index_list = []
        for i in range(df.shape[1]):
            if str(df.iloc[[0], [i]].values[0][0]) != str(df.columns[i]):
                index_list.append(str(df.columns[i]) + '(' + str(df.iloc[[0], [i]].values[0][0]) + ')')
            else:
                index_list.append(str(df.columns[i]))
        df.columns = index_list
        df.drop([0], axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)

    if df.empty or df.shape[1] == 1 or df.shape[0] <= 2:
        if if_strict:
            return None
        else:
            return df
    else:
        return df


# 若表头均为数字，则取第一行为表头
def change_df(df):
    for item in df.columns:
        if not str(item).isdigit():
            return df
    arr = df.values
    new_df = pd.DataFrame(arr[1:, 1:], index=arr[1:, 0], columns=arr[0, 1:])
    new_df.index.name = arr[0, 0]
    return new_df


iter_time = 0


# 对第一行进行检验
def first_column_check(df):
    global iter_time
    if df is None or df.empty:
        return None
    elif df.empty:
        return None
    if iter_time <= 10:
        if str(df.iat[0, 0]).isdigit() or '.' in str(df.iat[0, 0]) or '.' in str(df.iat[0, 0]) or str(
                df.iat[0, 0]) == '':
            new_index_list = []
            for item in df.columns[1:]:
                new_index_list.append(item)
            new_index_list.append(df.columns[0])
            df = df[new_index_list]
            iter_time += 1
            return first_column_check(df)
    iter_time = 0
    return df


# 对表头做校验
def index_check(df):
    if df is None or df.empty:
        return None
    elif df.empty:
        return None
    new_index_list = []
    if '名' in df.columns[0] or '标题' in df.columns[0]:
        return df
    if '日期' in df.columns[0] or '时间' in df.columns[0] or '年' in df.columns[0] or '数' in df.columns[0]:
        for item in df.columns[1:]:
            new_index_list.append(item)
        new_index_list.append(df.columns[0])
        df = df[new_index_list]
    for df_index in df.columns:
        if '名' in df_index or '标题' in df_index:
            new_index_list = [df_index]
            for item in df.columns:
                if item != df_index:
                    new_index_list.append(item)
            df = df[new_index_list]
            return df
    return df


def crawler_html_senlenium(url):
    options = Options()
    options.set_capability("acceptInsecureCerts", True)
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get(url)
    js = "var q=document.documentElement.scrollTop=100000"
    driver.execute_script(js)
    html = driver.page_source
    return html


async def crawler_html_pyppeteer(url):
    browser = await pyppeteer.launch(headless=True, args=['--disable-infobars'], ignoreHTTPSErrors=True)
    page = await browser.newPage()
    await page.setViewport({'width': 1920, 'height': 1080})
    await page.evaluateOnNewDocument('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')

    await page.goto(url)
    # await page.evaluate('_ => {window.scrollBy(0, window.innerHeight);}')
    await page.evaluate('_ => {window.scrollBy(0, 20000);}')
    await asyncio.sleep(10)
    html = await page.content()
    await browser.close()
    return html


def table_crawler(url: str, table_name='table', option='stdout', output_file_path='./', origin=False,
                  json_orient="columns", engine='requests', debug=False, process_list=None, max_empty_percentage=0.3,
                  min_similarity=0.7, if_strict=False):
    if process_list is None:
        process_list = ['brackets_remove', 'change_df', 'empty_column_remove', 'muti_index_process',
                        'first_column_check', 'index_check']
    time_start = time.time()
    # cc = OpenCC('t2s')
    html = None
    if engine == 'requests':
        html = crawler_html(url)
    elif engine == 'senlenium':
        html = crawler_html_senlenium(url)
    elif engine == 'pyppeteer':
        get_future = asyncio.ensure_future(crawler_html_pyppeteer(url))
        html = asyncio.get_event_loop().run_until_complete(get_future)
    # simple_query = cc.convert(table_name)
    simple_query = table_name
    try:
        if 'wiki' in url:
            # html_data = pd.read_html(html, attrs={'class': 'wikitable'})
            html_data = pd.read_html(html)
        else:
            html_data = pd.read_html(html)
    except Exception as e:
        print(e)
        return
    table_list = []
    # 去除相同的dataframe
    unrepeat_html_data = []
    if len(html_data) != 0:
        unrepeat_html_data.append(html_data[0])
    for item in html_data:
        repeat_flag = False
        for new_item in unrepeat_html_data:
            if item.equals(new_item):
                repeat_flag = True
                break
        if not repeat_flag:
            unrepeat_html_data.append(item)
    html_data = unrepeat_html_data
    # 去除相同的dataframe(快速版)
    # unrepeat_html_data = []
    # if len(html_data) != 0:
    #     last_item = html_data[0]
    #     unrepeat_html_data.append(last_item)
    #     for item in html_data:
    #         if item.equals(last_item):
    #             pass
    #         else:
    #             print("item:        ", item)
    #             print("last_item:        ", last_item)
    #             unrepeat_html_data.append(item)
    #             last_item = item
    # html_data = unrepeat_html_data

    for i, item in enumerate(html_data):
        table_data = pd.DataFrame(item)
        # 原始数据
        if origin:
            print("原始数据：    ")
            print(table_data)
        try:
            table_list.append(clean(table_data))
        except:
            table_list.append(table_data)

    # my processes for table_list

    # 如果列表表头是元组，则取第一项作为表头
    for item in table_list:
        if item is None or item.empty:
            continue
        index_list = []
        for item_index in item.columns:
            if isinstance(item_index, tuple):
                item_index = str(item_index[0])
            index_list.append(item_index)
        item.columns = index_list

    last_item_columns = []
    union_item_list = []
    res_list = []

    # 表格的合并
    for item in table_list:
        if item is None or item.empty:
            continue
        # 繁体转化为简体
        item = tradition_to_simple(item)

        # 对能够合并的表格进行合并，此处设置相似度大于70%进行合并
        union_item_columns = list(set(item.columns) & set(last_item_columns))
        similary_value = 2.0 * float(len(union_item_columns)) / (len(item.columns) + len(last_item_columns))
        if similary_value > min_similarity:
            union_item_list.append(item)
        else:
            if len(union_item_list) != 0:
                res_list.append(union_item_list)
            union_item_list = [item]
        last_item_columns = item.columns

    if len(union_item_list) != 0:
        res_list.append(union_item_list)
    table_list = []
    for item in res_list:
        table_list.append(pd.concat(item, ignore_index=True))

    # 对表格进行清洗
    clean_table_list = []
    for item in table_list:
        if item is None or item.empty:
            continue
        new_item = None
        # 去除其中的中括号、大括号、尖括号
        try:
            if debug:
                print("开始清洗表格：")
            if 'brackets_remove' in process_list:
                new_item = brackets_remove(item)
            if debug:
                print("移除冗余括号，得到：  ")
                print(new_item)
            if 'change_df' in process_list:
                new_item = change_df(new_item)
            if 'empty_column_remove' in process_list:
                new_item = empty_column_remove(new_item, max_empty_percentage, if_strict=if_strict)
            if debug:
                print("去除空列和信息过少的列，将数字表头删去，得到：  ")
                print(new_item)
            if 'muti_index_process' in process_list:
                new_item = muti_index_process(new_item, if_strict=if_strict)
            if debug:
                print("合并多行表头，得到：  ")
                print(new_item)
            if 'first_column_check' in process_list:
                new_item = first_column_check(new_item)
            if debug:
                print("对第一行信息进行校验，得到：  ")
                print(new_item)
            if 'index_check' in process_list:
                new_item = index_check(new_item)
            if debug:
                print("对表头信息进行校验，得到：  ")
                print(new_item)
        except Exception as e:
            print("when processing tables:  ", e)
        if new_item is not None:
            clean_table_list.append(new_item)
    table_list = clean_table_list

    # 出口处理
    if len(table_list) == 0:
        print("No table found with table_name: " + table_name + " !")
    else:
        if option == 'stdout':
            print("共计" + str(len(table_list)) + "张表格： ")
            for item in table_list:
                print(item)
        elif option == 'csv':
            if len(table_list) == 1:
                table_list[0].to_csv(output_file_path + str(simple_query).replace('/', '_') + '.csv', encoding='utf-8',
                                     index=False)
            else:
                i = 0
                for item in table_list:
                    i += 1
                    item.to_csv(output_file_path + str(simple_query).replace('/', '_') + '_' + str(i) + '.csv',
                                encoding='utf-8', index=False)
        elif option == 'excel':
            if len(table_list) == 1:
                table_list[0].to_excel(output_file_path + str(simple_query).replace('/', '_') + '.xlsx',
                                       encoding='utf-8',
                                       index=False)
            else:
                i = 0
                for item in table_list:
                    i += 1
                    item.to_excel(output_file_path + str(simple_query).replace('/', '_') + '_' + str(i) + '.xlsx',
                                  encoding='utf-8', index=False)
        elif option == 'json':
            if len(table_list) == 1:
                table_list[0].to_json(output_file_path + str(simple_query).replace('/', '_') + '.json',
                                      force_ascii=False,
                                      orient=json_orient)
            else:
                i = 0
                for item in table_list:
                    i += 1
                    item.to_json(output_file_path + str(simple_query).replace('/', '_') + '_' + str(i) + '.json',
                                 force_ascii=False, orient=json_orient)

    time_end = time.time()
    if debug:
        print("共计用时：" + str(time_end - time_start) + 's')


if __name__ == '__main__':
    table_crawler('https://zh.wikipedia.org/zh-cn/%E6%BC%AB%E5%A8%81%E7%94%B5%E5%BD%B1%E5%AE%87%E5%AE%99', origin=True, engine="senlenium")
