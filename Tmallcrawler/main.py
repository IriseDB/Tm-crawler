import json
import time
import csv,os
from DrissionPage import *
import re

def write_to_csv(*args):
    filename = f'波场.csv'
    #title, classtype, mallarea, urlscd,addr,tel
    headers = ['json']
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # 写入表
    data = [] # 标题行（可选）
    for arg in args:
        data.append(arg)

    with open(filename, mode='a', newline='',encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def remove_first_left_and_last_right_parentheses(s):
    # 移除第一个左括号 `(` 及其前面的内容
    s = re.sub(r'^.*?\(', '', s, count=1)
    # 移除最后一个右括号 `)` 及其后面的内容
    s = re.sub(r'\)[^)]*$', '', s, count=1)
    return s

def extract_values(data, key):
    """
    递归遍历 JSON 数据，提取所有指定键的值。
    参数:
    data (dict or list): JSON 数据对象，可以是字典或列表。
    key (str): 需要提取的键名。

    返回:
    list: 包含所有找到的指定键的值。
    """
    values = []
    if isinstance(data, dict):
        # 遍历字典中的所有键值对
        
        for k, v in data.items():
            if k == key:
                values.append(v)
            # 递归遍历字典嵌套
            values.extend(extract_values(v, key))
    elif isinstance(data, list):
        # 遍历列表中的所有元素
        for item in data:
            values.extend(extract_values(item, key))
    
    return values
page=ChromiumPage()

def work(url):
    page.listen.start('mtop.taobao.pcdetail.data.get')
    page.get(url)
    data=page.listen.wait(1,timeout=10).response.body
    Data=json.loads(remove_first_left_and_last_right_parentheses(data))
    dic={}
    # 价格
    prices=extract_values(Data,'sku2info')[0]
    pr={}
    skus=extract_values(Data,'skus')[0]
    pid=extract_values(Data,'pid')[0]
    values=extract_values(Data,'values')[0]
    for value in values:
        for sku in skus:
            if sku['propPath']==f"{pid}:{value['vid']}":
                result = prices[sku['skuId']].get('price') or prices[sku['skuId']].get('subPrice', '')
                pr[value['name']]=result.get('priceText','')
    dic['价格']=pr
    # 标题
    dic['标题']=page.ele('@tag()=h1').text
    # 主图
    imgs=(extract_values(Data,'headImageVO')[0]['images'])
    dic['主图']=imgs
    itemss=(extract_values(Data,'extensionInfoVO')[0]['infos'])
    for items1 in itemss:
        try:
            items=items1['items']
            for item in items:
                try:
                    if item['title']=='医疗器械产品名称':
                        dic['医疗器械产品名称']=item['text']
                    if item['title']=='注册证号':
                        dic['注册证号']=item['text']
                    if item['title']=='品牌':
                        dic['品牌']=item['text']
                    if item['title']=='颜色分类':
                        dic['颜色分类']=item['text']
                except:
                    pass
        except:
            pass
    #图文详情
    descimgs=(page.ele('@@class=desc-root@@id=content').eles('@tag()=img').get.attrs('data-src'))
    dic['图文详情']=descimgs
    print(dic)
    write_to_csv(dic)#数据存入csv

if __name__ == '__main__':
    input('等待登录后输入任意')
    f=open('urls.txt', 'r')
    urls=f.readlines()
    for url in urls:
        time.sleep(5)
        url=url.strip()
        work(url)

        # work('https://detail.tmall.com/item.htm?spm=a21n57.1.item.1.4376523cZ4jbZS&priceTId=2100c81d17312409212464179e0b7d&utparam=%7B%22aplus_abtest%22%3A%228e63e6e0d9395fcddca0975864358003%22%7D&id=707831057450&ns=1&xxc=ad_ztc&skuId=4969684684617')