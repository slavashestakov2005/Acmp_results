import os
import pickle
from datetime import datetime


class Task:
	def __init__(self, id, good, bad):
		self.id, self.good, self.bad = id, good, bad
		self.good_langs, self.bad_langs = {}, {}

	def status(self):
		return self.good > 0

	def solve(self, lang):
		if 'C++' in lang:
			lang = 'C++'
		self.good += 1
		if lang not in self.good_langs:
			self.good_langs[lang] = 0
		self.good_langs[lang] += 1

	def solved(self, lang=None):
		if lang is None:
			return self.good
		return self.good_langs[lang] if lang in self.good_langs else 0

	def unsolve(self, lang):
		if 'C++' in lang:
			lang = 'C++'
		self.bad += 1
		if lang not in self.bad_langs:
			self.bad_langs[lang] = 0
		self.bad_langs[lang] += 1

	def unsolved(self, lang=None):
		if lang is None:
			return self.bad
		return self.bad_langs[lang] if lang in self.bad_langs else 0

	@staticmethod
	def sortf(task):
		return task.id

	def pm(self, lang=None):
		result, good, bad = '', self.solved(lang), self.unsolved(lang)
		if good > 0:
			result += '{}+'.format(good)
			if bad > 0:
				result += ', '
		if bad > 0:
			result += '{}-'.format(bad)
		return result

	def __repr__(self):
		task_id = ''.join(map(str, self.id)) if type(self.id) == tuple else str(self.id)
		return '{} ({})'.format(task_id, self.pm())


def load_saved(raw_file):
	if not os.path.exists(raw_file):
		return [], [], -1
	with open(raw_file, 'rb') as f:
		data = pickle.load(f)
	return data


def dump_saved(raw_file, *args):
	with open(raw_file, 'wb') as f:
		pickle.dump(args, f)


def get_time():
	return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def writable_md_task(time, data, task):
	result = '''# Задачи {}
Время обновления: {}
| acmp  | codeforces | Участник | +    | -    |
| ----- | ---------- | -------- | ---- | ---- |
'''.format(task, time)
	for i in range(1, len(data[0])):
		result += '| {} | {} | {} | {} | {} |\n'.format(data[1][i][1], data[2][i][1], data[0][i][1], data[3][i][1], data[4][i][1])
	return result
