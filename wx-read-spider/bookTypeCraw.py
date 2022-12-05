import csv
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor
import requests
from getHomeStoreModul import getHomeStoreModule

# 不重复，完整性，可续接爬取，存储数据库或CSV记录

# 书名
# 分类
# 最大免费章节  maxFreeChapter
# 推荐值   newRating
# 出版时间
# 介绍
# 图片
# 推荐值

# 基础设置
isThreadPool = False  # 是否开启多线程池
ThreadPoolNum = 5  # 线程池数量
exportDict = {  # 需导出字段

}


def getWXBooks(booksId, queryPath):
    bookList = []
    for i in range(10000):
        maxIndex = i * 20
        rTime = random.randint(1, 3)  # 随机延迟，从1到3内取一个整数值
        time.sleep(rTime)  # 把随机取出的整数值传到等待函数中
        res = requests.get(
            queryPath, params={'maxIndex': maxIndex})
        books = res.json()['books']
        if len(books):
            for book in books:
                bookList.append(book)
        hasMore = res.json()['hasMore']
        if hasMore == 0: break
    return bookList


def writeCSV(bookInfo, path):
    with open(path, 'w', encoding='UTF8', newline='') as f:
        fieldnames = ['title', 'publishTime', 'category', 'intro', 'maxFreeChapter', 'newRating', 'free',
                      'price',
                      'cover']
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval='intro', extrasaction='ignore')

        # 写入头
        writer.writeheader()

        for book in bookInfo:
            # 写入数据
            writer.writerow(book['bookInfo'])


def getWXBookTypeList(bookInfo):
    parentPath = r'bookTypeSearchInfo\{dirName}'.format(
        dirName=bookInfo['title'])
    if not os.path.exists(parentPath):
        os.mkdir(parentPath)
    for t in bookInfo['sublist']:
        subPath = r'{parentPath}\{csvName}-{totalCount}.csv'.format(
            parentPath=parentPath, csvName=t['title'], totalCount=t['totalCount'])
        hasSubFile = os.path.exists(subPath)
        if not hasSubFile:
            #   todo totalCount不同时进行对比重复项增量插入,防止新创建文件   ?
            #   如何获取totalCount所有书籍  1.不断调取然后去重  以excel中2次查询非重复项 80左右为例，一个子集至少需要该(totalCount / 80)次才能读取完整 ，直到csv中数据数量和totalCount相同
            path = 'https://weread.qq.com/web/bookListInCategory/{booksId}}'.format(booksId=t['CategoryId'])
            bookData = getWXBooks(t['CategoryId'], path)
            writeCSV(bookData, subPath)
        #   todo  mongodb  redis  数据库存储


def thread_pool(sub_f, list1):
    executor = ThreadPoolExecutor(5)
    all_results = executor.map(sub_f, list1)
    return all_results


if __name__ == '__main__':
    homeStore = getHomeStoreModule()
    BookIds = homeStore['categories']
    start = time.time()
    if isThreadPool:
        results = thread_pool(getWXBookTypeList, BookIds)
    else:
        for i in BookIds:
            getWXBookTypeList(i)
    end = time.time()
