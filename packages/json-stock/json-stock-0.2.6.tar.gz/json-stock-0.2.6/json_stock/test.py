
# json_stock [json_stock]

import sys
from sout import sout
from ezpip import load_develop
# json_stock [json_stock]
jst = load_develop("json_stock", "../", develop_flag = True)

# # トランザクションによる競合編集防止のテスト
# test_db = jst.JsonStock("./test_db/")
# if "test_table" not in test_db: test_db["test_table"] = {}
# table = test_db["test_table"]
# table["test_key"] = "hoge"
# with test_db["test_table"].lock("test_key") as rec:
# 	rec.value = input("input_value>>")
# sys.exit()

# open DB
test_db = jst.JsonStock("./test_db/")
print(test_db)
# create table
test_db["test_table"] = {}
# get table
test_table = test_db["test_table"]
# create new value
test_table["test"] = {"hello": "world!"}
# transaction (record lock)
with test_table.lock("test") as rec:	# lock the "test" key
	rec.value["hello"] += "!!"
# read value
print(test_table["test"])
# show table
print(test_table)
# transaction example 2 (without with)
rec = test_table.lock("test")
rec.value = "hoge"
rec.unlock()
print(test_table["test"])
# transaction example 3 (without with)
rec = test_table.lock("test")
rec.value = "fuga"
test_table.unlock("test")
print(test_table["test"])
# iterate (listup all keys in the table)
print([key for key in test_table])
# delete value
del test_table["test"]
# delete table
del test_db["test_table"]
