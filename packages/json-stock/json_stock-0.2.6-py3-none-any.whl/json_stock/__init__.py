
import os
import sys
import fies
import json
import hashlib
import rename_lock
from sout import sout, souts

# 索引が存在するか調べる (編集中も含む)
def check_index_exists(db_dir):
	for filename in fies[db_dir]:
		if filename.startswith("index.json"): return True
	return False

# DBディレクトリが存在しないときに作成
def make_db_dir(db_dir):
	# ディレクトリが存在しない場合に作成
	if os.path.exists(db_dir) is False: os.mkdir(db_dir)
	# 索引が存在しない場合に作成
	if check_index_exists(db_dir) is False:	# 索引が存在するか調べる (編集中も含む)
		index_filename = os.path.join(db_dir, "index.json")
		fies[index_filename] = {}
	# dataディレクトリが存在しない場合に作成
	data_dir = os.path.join(db_dir, "data")
	if os.path.exists(data_dir) is False: os.mkdir(data_dir)

# key文字列をhashに変換
def gen_hash(table_name, key):
	# 2値をつなげた文字列を作成
	dkey_obj = [table_name, key]
	dkey = json.dumps(dkey_obj, ensure_ascii = False)
	# ハッシュ化
	bin_dkey = dkey.encode()
	hash_key = hashlib.sha256(bin_dkey).hexdigest()
	return hash_key

# locked record クラス
class LockedRecord:
	# 初期化処理
	def __init__(self, table, key):
		self.table = table
		self.key = key
		# lockされたファイルからvalueの読み出し
		rlock = self.table._rlock_dic[self.key]
		self.value = fies[rlock.filename, "json"]
	# with構文内に入る処理
	def __enter__(self):
		return self
	# with構文から脱出する処理
	def __exit__(self, ex_type, ex_value, trace):
		self.unlock()	# ロック解除
	# 手動unlock
	def unlock(self):
		# 書き込み対象ファイルを取得して書き込む (すでにlockされている)
		rlock = self.table._rlock_dic[self.key]
		fies[rlock.filename, "json"] = self.value
		# valueが入っているファイルのlockを解除取得
		rlock.unlock()
	# 文字列化
	def __str__(self):
		return "<json_stock LockedRecord (table: %s, key: %s)>"%(
			self.table.table_name, self.key)
	# 文字列化_その2
	def __repr__(self):
		return str(self)

# テーブルクラス
class Table:
	# 初期化処理
	def __init__(self, table_name, db):
		self.table_name = table_name
		self.db = db	# 属しているDB
		self._rlock_dic = {}	# lock済みvalueのrename_lockオブジェクトの辞書
		self._locked_rec_dic = {}	# lock中recordオブジェクトの辞書
	# valueの読み出し (Read)
	def __getitem__(self, key):
		# 存在するかどうかを確認
		if key not in self:
			raise Exception("[json_stock error] The key '%s' does not exist."%key)
		# 値のファイルの読み出し (readの場合でも、writeロック中は読めないべきであるので、rename_lockを利用する)
		hash_key = gen_hash(self.table_name, key)	# key文字列をhashに変換
		filename = os.path.join(self.db.db_dir, "data", "%s.json"%hash_key)
		with rename_lock(filename) as rlock:	# 競合編集防止
			value = fies[rlock.filename, "json"]
		return value
	# valueの新規作成/上書き (Create / Update)
	def __setitem__(self, key, value):
		# 新規作成の場合
		if key not in self:
			# 値のファイルの名前
			hash_key = gen_hash(self.table_name, key)	# key文字列をhashに変換
			filename = os.path.join(self.db.db_dir, "data", "%s.json"%hash_key)
			# 索引登録・値ファイルの作成
			index_filename = os.path.join(self.db.db_dir, "index.json")
			with rename_lock(index_filename) as rlock:	# 競合編集防止
				index = fies[rlock.filename, "json"]
				index[self.table_name][key] = True
				fies[rlock.filename, "json"] = index
				fies[filename, "json"] = None	# 値ファイルの作成
		# valueの書き込み
		with self.lock(key) as rec:	# トランザクション処理 (レコードのロック)
			rec.value = value
	# keyの存在確認
	def __contains__(self, key):
		# 索引を調べる
		index_filename = os.path.join(self.db.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
		# 存在するかどうかを返す
		return (key in index[self.table_name])
	# valueの削除 (Delete)
	def __delitem__(self, key):
		# 存在するかどうかを確認
		if key not in self:
			raise Exception("[json_stock error] The key '%s' does not exist."%key)
		# 索引から削除
		index_filename = os.path.join(self.db.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
			del index[self.table_name][key]
			fies[rlock.filename, "json"] = index
		# 値のファイルの削除
		hash_key = gen_hash(self.table_name, key)	# key文字列をhashに変換
		filename = os.path.join(self.db.db_dir, "data",
			"%s.json"%hash_key)
		os.remove(filename)
	# keyのイテレート (for 文脈への対応)
	def __iter__(self):
		# 索引を利用
		index_filename = os.path.join(self.db.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
		for key in index[self.table_name]:
			yield key
	# トランザクション処理 (レコードのロック)
	def lock(self, key):
		# valueが入っているファイルのlockを取得
		hash_key = gen_hash(self.table_name, key)	# key文字列をhashに変換
		filename = os.path.join(self.db.db_dir, "data", "%s.json"%hash_key)
		if key in self:
			self._rlock_dic[key] = rename_lock(filename)
		else:
			# レコードが元々存在しない場合
			index_filename = os.path.join(self.db.db_dir, "index.json")
			index_rlock = rename_lock(index_filename)	# 競合編集防止
			index = fies[index_rlock.filename, "json"]
			index[self.table_name][key] = True
			fies[index_rlock.filename, "json"] = index
			fies[filename, "json"] = None	# valueのファイルの作成
			# ロックが解除されている瞬間がないように逆順で ロック→解除 する
			self._rlock_dic[key] = rename_lock(filename)
			index_rlock.unlock()
		# locked record オブジェクトを返す (このlock recordがunlockされたときにfileもunlockする)
		l_rec = LockedRecord(self, key)
		self._locked_rec_dic[key] = l_rec	# lock中recordオブジェクトの辞書に記録
		return l_rec
	# レコードのロック解除
	def unlock(self, key):
		# 未lockレコードのunlock()エラー
		if key not in self._locked_rec_dic: raise Exception("[json_stock error] This record is not locked or this process does not have a lock on this record.")
		# lock中recordオブジェクトのunlock()を呼ぶ
		self._locked_rec_dic[key].unlock()
		# table内での記録を消す
		del self._locked_rec_dic[key]
	# 文字列化
	def __str__(self):
		return souts(self)	# soutがjson-stockの可視化に公式に対応している
	# 文字列化_その2
	def __repr__(self):
		return str(self)
	# レコード数
	def __len__(self):
		# 索引から調べる
		index_filename = os.path.join(self.db.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
		return len(index[self.table_name])

# データベースクラス
class JsonStock:
	# 初期化処理
	def __init__(self, db_dir):
		# DBディレクトリが存在しないときに作成
		make_db_dir(db_dir)
		self.db_dir = db_dir
	# 新規テーブル作成
	def __setitem__(self, table_name, value):
		# すでにテーブルが存在する場合
		if table_name in self:
			raise Exception("[json_stock error] Creation of new table failed. (The table '%s' already exists.)"%table_name)
		# value が空辞書出ない場合
		if value != {}:
			raise Exception("[json_stock error] Creation of new table failed. (Value must be an empty dictionary like '{{}}'.)")
		# 新規テーブル登録
		index_filename = os.path.join(self.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
			index[table_name] = {}
			fies[rlock.filename, "json"] = index
	# テーブルの取得
	def __getitem__(self, table_name):
		# テーブルの存在確認
		if table_name not in self:
			raise Exception("[json_stock error] The table '%s' does not exist."%table_name)
		# テーブルオブジェクトを返す
		return Table(table_name, db = self)
	# テーブルの存在確認
	def __contains__(self, table_name):
		# 索引を取得
		index_filename = os.path.join(self.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
		return (table_name in index)
	# tableの削除 (Delete)
	def __delitem__(self, table_name):
		# 存在するかどうかを確認
		if table_name not in self:
			raise Exception("[json_stock error] The table '%s' does not exist."%table_name)
		# テーブルに残存するレコードをすべて削除
		table = self[table_name]
		for key in table: del table[key]
		# 索引から削除
		index_filename = os.path.join(self.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
			del index[table_name]
			fies[rlock.filename, "json"] = index
	# tableのイテレート (for 文脈への対応)
	def __iter__(self):
		# 索引を利用
		index_filename = os.path.join(self.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
		for table_name in index:
			yield table_name
	# 文字列化
	def __str__(self):
		return souts(self)	# soutがjson-stockの可視化に公式に対応している
	# 文字列化_その2
	def __repr__(self):
		return str(self)
	# テーブル数
	def __len__(self):
		# 索引の規模
		index_filename = os.path.join(self.db_dir, "index.json")
		with rename_lock(index_filename) as rlock:	# 競合編集防止
			index = fies[rlock.filename, "json"]
		return len(index)
