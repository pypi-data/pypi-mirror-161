
# ファイル入出力ツール [fies]

import os
import sys
import json

# read_modeを表すオブジェクト
class _ReadMode:
	# 初期化処理
	def __init__(self):
		pass

# テキストファイルの読み込み
def text_read(filename, **kw_args):
	with open(filename, "r", encoding = "utf-8") as f:
		data = f.read()
	return data

# テキストファイルの書き出し
def text_write(filename, data, **kw_args):
	with open(filename, "w", encoding = "utf-8") as f:
		f.write(data)

# jsonファイルの読み込み
def json_read(filename, **kw_args):
	json_str = text_read(filename, **kw_args)	# テキストファイルの読み込み
	return json.loads(json_str)

# jsonファイルの書き出し
def json_write(filename, data, **kw_args):
	json_str = json.dumps(data, indent = 4, ensure_ascii = False)
	text_write(filename, json_str, **kw_args)	# テキストファイルの書き出し

# ファイル入出力ツール [fies]
class Fies:
	# 初期化処理
	def __init__(self):
		pass
	# ファイル読み書き
	def __call__(self, filename, data = _ReadMode(), file_format = "auto", **kw_args):
		if type(data) == _ReadMode:
			# 読み込み
			return self._read(filename, file_format, **kw_args)
		else:
			# 書き出し
			self._write(filename, data, file_format, **kw_args)
	# ファイルの読み込み (略記)
	def __getitem__(self, query):
		filename = query
		basename, ext = os.path.splitext(filename)
		if ext == ".json":
			return self(filename, file_format = "json")
		else:
			return self(filename, file_format = "text")
	# ファイルの保存 (略記)
	def __setitem__(self, query, data):
		filename = query
		basename, ext = os.path.splitext(filename)
		if ext == ".json":
			self(filename, data, file_format = "json")
		else:
			self(filename, data, file_format = "text")
	# 読み込み
	def _read(self, filename, file_format, **kw_args):
		if file_format == "json":
			return json_read(filename, **kw_args)	# jsonファイルの読み込み
		elif file_format == "text":
			return text_read(filename, **kw_args)	# テキストファイルの読み込み
		else:
			raise Exception("[fies error] ext is not supported.")
	# 書き出し
	def _write(self, filename, data, file_format, **kw_args):
		if file_format == "json":
			json_write(filename, data, **kw_args)	# jsonファイルの書き出し
		elif file_format == "text":
			text_write(filename, data, **kw_args)	# テキストファイルの書き出し
		else:
			raise Exception("[fies error] ext is not supported.")

# 呼び出しの準備
fies = Fies()	# Fies型のオブジェクトを予め実体化
sys.modules[__name__] = fies	# モジュールオブジェクトとfiesオブジェクトを同一視
