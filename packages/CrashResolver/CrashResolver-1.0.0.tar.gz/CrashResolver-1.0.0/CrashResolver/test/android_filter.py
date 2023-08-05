'''
统计指定时间范围的crash分类
'''

import re
from ..android import main
from ..database_csv import load

records = load('db_android.csv')
pattern = re.compile("'2022-07-[15|16|17|18|19|20].*")
lists = list(record for record in records if pattern.match(
    record['Start time']))
main.group_detail(lists, lambda x: x['stack_key'], 'stack_key')
