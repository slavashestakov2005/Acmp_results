import requests
from utils import *
import re
import time


class User:
	def __init__(self, handle, rating):
		self.handle, self.rating = handle, rating

	@staticmethod
	def sortf(user):
		return user.rating

	def set_name(self, name):
		self.name = name

	def writable(self):
		return 'Хендл: {}\nРейтинг: {}\nПосылок: {}\n'.format(self.handle, self.rating, self.send)

	def writable_md(self):
		return '| {} | {} | {} |'.format(self.handle, self.name, self.rating, self.send)


class Tasks:
	def __init__(self, bad_with_lang, good_with_lang):
		bad, good = [_[0] for _ in bad_with_lang], [_[0] for _ in good_with_lang]
		self.map_tasks = {_: Task(_, 0, 0) for _ in set(bad).union(good)}
		self.max_task = (0, '')
		for task in good_with_lang:
			self.map_tasks[task[0]].solve(task[1])
		for task in bad_with_lang:
			self.map_tasks[task[0]].unsolve(task[1])
		self.good, self.bad = 0, 0
		self.tasks = self.map_tasks.values()
		for task in self.tasks:
			self.max_task = max(self.max_task, task.id)
			if task.status():
				self.good += 1
			else:
				self.bad += 1

	def get_task(self, task):
		if type(task) == str:
			parse = re.findall(r'(\d+)\s*(\D+)', task)[0]
			task = int(parse[0]), parse[1]
		if task not in self.map_tasks:
			return Task(task, 0, 0)
		return self.map_tasks[task]

	def writable(self, last_solve):
		result = 'Всего решено {}\n'.format(self.good)
		result += 'Всего не решено {}\n'.format(self.bad)
		result += 'Последняя попытка: {}\n'.format(last_solve)
		tasks = {}
		for task in self.tasks:
			part = (task.id[0] - 1) // 100
			if part not in tasks:
				tasks[part] = [[], []]
			if task.status():
				tasks[part][0].append(task)
			else:
				tasks[part][1].append(task)
		tasks = sorted(tasks.items(), key=lambda x: x[0])
		for part in tasks:
			p, t = part
			result += '\nКонтесты {} — {}:\n'.format(p * 100 + 1, p * 100 + 100)
			good = sorted(t[0], key=Task.sortf)
			bad = sorted(t[1], key=Task.sortf)
			result += 'Решено ({}): {}\n'.format(len(good), str(good)[1:-1])
			result += 'Не решено ({}): {}\n'.format(len(bad), str(bad)[1:-1])
		return result

	def writable_md(self):
		return ' {} | {} |\n'.format(self.good, self.bad)

	def writable_txt(self):
		return '\t{}\t   {}\t\n'.format(self.good, self.bad)


def parse_user_profile(handle):
	url = 'https://codeforces.com/api/user.info?handles={}'.format(handle)
	info = requests.get(url).json()['result'][0]
	if 'rating' not in info:
		rating = 0
	else:
		rating = info['rating']
	return User(handle, rating)


def parse_user_submissions(handle, raw_file):
	bad_task, good_task, last_solve = load_saved(raw_file)
	first_solve = last_solve
	task_per_page = 5
	page = 0
	while True:
		print('Cf page', page)
		url = 'https://codeforces.com/api/user.status?handle={}&from={}&count={}'.format(handle, 1 + page * task_per_page, task_per_page)
		time.sleep(1)
		data = requests.get(url)
		rows = data.json()['result']
		print(len(rows))
		for sub in rows:
			prob = sub['problem']
			id, task, lang, res = sub['id'], (prob['contestId'], prob['index']), sub['programmingLanguage'], sub['verdict']
			if first_solve == last_solve:
				first_solve = id
			if id == last_solve:
				rows = []
				break
			if res == 'OK':
				good_task.append([task, lang])
			else:
				bad_task.append([task, lang])
		print(len(rows))
		if len(rows) < task_per_page:
			break
		page += 1
	dump_saved(raw_file, bad_task, good_task, first_solve)
	return Tasks(bad_task, good_task), len(good_task) + len(bad_task), first_solve


def writable_md(time, data):
	result = '''# Результаты codeforces
Здесь можно увидеть результаты решения задач на сайте [codeforces](https://codeforces.com). 

## Результаты
Все решенные задачи можно увидеть в `codeforces_results.xlsx`.   
Свои результаты можно посмотреть в папке `codeforces_results`.  
Домашняя работа написана в папке `tasks`, а её выполнение в папке `tasks_results`.

## Таблица
Время обновления: {}
| Хендл | Участник | Рейтинг | Посылки | +    | -    |
| ----- | -------- | ------- | ------- | ---- | ---- |
'''.format(time)
	for x in data:
		result += x[0].writable_md() + x[1].writable_md()
	return result
