# json_stock

下の方に日本語の説明があります

## Overview
- JSON-based database
- Very simple to operate, but fast, and supports parallel processing.
- DB itself behaves like "one big JSON"
- description is under construction.

## Usage
```python
import json_stock as jst

# open DB
test_db = jst.JsonStock("./test_db/")
print(test_db)
# create table
test_db["test_table"] = {}
# get table
test_table = test_db["test_table"]
print(test_table)
# create new value
test_table["test"] = {"hello": "world!!"}
# read value
print(test_table["test"])
# show table
print(test_table)
# iterate (listup all keys in the table)
print([key for key in test_table])
# delete value
del test_table["test"]
# delete table
del test_db["test_table"]
```

- Advanced: transaction
	- If the following is written, the "test" key is locked in the "WITH" syntax, and other processes cannot change the value of the key until the program emerges from the "WITH" syntax.
	- However, this lock occurs on a per-key basis, not per-table basis, so other keys can be edited without any problem while the program is executing the "WITH" syntax.
```python
# lock the "test" key
with test_table.lock("test") as rec:
	rec.value["new_key"] = "hell"
	rec.value["hello"] += "!!"
```
- If you rewrite rec.value in "WITH" as you like, the rec.value value at the moment of leaving "with" is automatically reflected in the DB ("commit" in general DB).

- Example of locking multiple keys
```python
# lock the "test" key
with test_table.lock("test") as rec, test_table.lock("test2") as rec2:
	rec.value["hello"] += "!!"
	rec2.value["new_key"] = rec.value["hello"] + "hell"	# This prevents unintentional rewriting of rec just before changing rec2, and can be used for complex transactions such as money transfer processing
```

- Example without "WITH" syntax - Example 1
```python
rec = test_table.lock("test")
rec.value = "hoge"
rec.unlock()
```

- Example without "WITH" syntax - Example 2
```python
rec = test_table.lock("test")
rec.value = "fuga"
test_table.unlock("test")
```

- NG Example: DO NOT write like this
```python
with test_table.lock("test") as rec:
	test_table["test"] = "hoge"	# NG
```
- In the above example, the edit of the "test" key is locked in with, so if you try to edit the value via test_table, the lock is not released forever and the program freezes.
- It is correct to write as follows
```python
with test_table.lock("test") as rec:
	rec.value = "hoge"	# OK
```
- The rec object is given special permission to edit the "test" key in the "WITH" syntax, so it can only edit that data through rec.value while it is locked.


## 概要
- JSONベースのデータベース
- 操作が非常に単純だが、高速で、並列処理にも対応
- DB自体が「1つの大きなJSON」のように振る舞う

## 使用例
```python
import json_stock as jst

# DBを開く (存在しない場合はディレクトリが自動的に作成される)
test_db = jst.JsonStock("./test_db/")
print(test_db)
# テーブルの作成 (右辺は必ず空の辞書である必要がある)
test_db["test_table"] = {}
# テーブルの取得
test_table = test_db["test_table"]
print(test_table)
# テーブルの"test"キーにデータを登録 (すでにキーが存在する場合は上書き)
test_table["test"] = {"hello": "world!!"}
# テーブルの"test"キーに束縛されたデータを読み出す
print(test_table["test"])
# テーブルの可視化 (soutを用いれば表示レコード数上限もカスタマイズ可能)
print(test_table)
# for文脈でテーブルの全キーを巡回
print([key for key in test_table])
# "test"キーの値を削除
del test_table["test"]
# テーブルの削除
del test_db["test_table"]
```

- 発展的な例: トランザクション処理
	- 下記のように書くと、with構文内で"test"キーがロックされ、withから脱出するまでは他のプロセスが当該キーの値を変更できなくなる
	- ただしこのロックはtable単位ではなく、キー単位で発生するので、withの間も他のkeyは問題なく編集できる
```python
# "test"キーをロックする
with test_table.lock("test") as rec:
	rec.value["new_key"] = "hell"
	rec.value["hello"] += "!!"
```
- with内でrec.valueを好きなように書き換えると、withを抜けた瞬間のrec.value値が自動的にDBに反映される (一般的なDBでいうところの「コミット」)

- 複数のkeyをロックする例
```python
# lock the "test" key
with test_table.lock("test") as rec, test_table.lock("test2") as rec2:
	rec.value["hello"] += "!!"
	rec2.value["new_key"] = rec.value["hello"] + "hell"	# このように書けば、rec2を変更する直前に意図せずrecが書き換わってしまう等が防げるため、送金処理などの複雑なトランザクションにも利用できる
```

- with構文を使わない例 - その1
```python
rec = test_table.lock("test")
rec.value = "hoge"
rec.unlock()
```

- with構文を使わない例 - その2
```python
rec = test_table.lock("test")
rec.value = "fuga"
test_table.unlock("test")
```

- NG例: 下記のような書き方をしてはいけない
```python
with test_table.lock("test") as rec:
	test_table["test"] = "hoge"	# NG
```
- 上記の例では、with内において"test"keyの編集がロックされているため、test_table経由で値の編集を試みると、永遠にロックが解除されず、フリーズする
- 下記のように書くのが正しい
```python
with test_table.lock("test") as rec:
	rec.value = "hoge"	# OK
```
- recオブジェクトは、with構文内において、"test"キーを編集する特別な権限を与えられているため、ロック中はrec.valueを通じてのみ当該データを編集することができる
