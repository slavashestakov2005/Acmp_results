import requests
from bs4 import BeautifulSoup
from utils import *


class User:
	def __init__(self, id, name, rank, rating):
		self.id, self.name, self.rank, self.rating = id, name, rank, rating

	@staticmethod
	def sortf(user):
		return user.rank

	def set_name(self, name):
		self.name = name

	def writable(self):
		return 'ID: {}\nБаллы: {}\nМесто: {}\nПосылок: {}\n'.format(self.id, self.rating, self.rank, self.send)

	def writable_md(self):
		return '| {} | {} | {} | {} | {} |'.format(self.id, self.name, self.rank, self.rating, self.send)

	def writable_txt(self):
		return '{}\t{}{}\t{}\t{}'.format(self.id, self.name + ' ' * max(0, 25 - len(self.name)), self.rank, self.rating, self.send)


class Tasks:
	def __init__(self, bad_with_lang, good_with_lang):
		bad, good = [_[0] for _ in bad_with_lang], [_[0] for _ in good_with_lang]
		self.map_tasks = {_: Task(_, 0, 0) for _ in set(bad).union(good)}
		self.max_task = 0
		for task in good_with_lang:
			self.map_tasks[task[0]].solve(task[1])
		for task in bad_with_lang:
			self.map_tasks[task[0]].unsolve(task[1])
		self.good, self.bad, self.goods, self.bads = 0, 0, 0, 0
		self.tasks = self.map_tasks.values()
		for task in self.tasks:
			self.max_task = max(self.max_task, task.id)
			if task.id <= 1000:
				if task.status():
					self.goods += 1
				else:
					self.bads += 1
			else:
				if task.status():
					self.good += 1
				else:
					self.bad += 1

	def get_task(self, task):
		if task not in self.map_tasks:
			return Task(task, 0, 0)
		return self.map_tasks[task]

	def writable(self, last_solve):
		result = 'Всего решено {}, из них в первой тысяче {}\n'.format(self.good + self.goods, self.goods)
		result += 'Всего не решено {}, из них в первой тысяче {}\n'.format(self.bad + self.bads, self.bads)
		result += 'Последняя попытка: {}\n'.format(last_solve)
		tasks = {}
		for task in self.tasks:
			part = (task.id - 1) // 100
			if part not in tasks:
				tasks[part] = [[], []]
			if task.status():
				tasks[part][0].append(task)
			else:
				tasks[part][1].append(task)
		tasks = sorted(tasks.items(), key=lambda x: x[0])
		for part in tasks:
			p, t = part
			result += '\nЗадачи {} — {}:\n'.format(p * 100 + 1, p * 100 + 100)
			good = sorted(t[0], key=Task.sortf)
			bad = sorted(t[1], key=Task.sortf)
			result += 'Решено ({}): {}\n'.format(len(good), str(good)[1:-1])
			result += 'Не решено ({}): {}\n'.format(len(bad), str(bad)[1:-1])
		return result

	def writable_md(self):
		return ' {} | {} | {} | {} |\n'.format(self.goods, self.bads, self.goods + self.good, self.bads + self.bad)

	def writable_txt(self):
		return '\t{}\t   {}\t\t{}\t{}\n'.format(self.goods, self.bads, self.goods + self.good, self.bads + self.bad)


def parse_user_profile(userId):
	url = 'https://acmp.ru/?main=user&id={}'.format(userId)
	r = requests.get(url)
	html_parser = BeautifulSoup(r.text, 'html.parser')
	rank = html_parser.find_all('b', {'class' : 'btext'})[0]
	rank = int(rank.text.split()[1])
	rating = html_parser.find_all('b', {'class' : 'btext'})[1]
	rating = int(rating.text.split()[1])
	userName = html_parser.find_all('td', {'class' : 'menu_title'})[4].text
	userName = bytes(userName, r.encoding).decode('cp1251').title()
	userName = ' '.join(userName.split(' ')[0:2])
	return User(userId, userName, rank, rating)


def parse_user_submissions(userId, raw_file):
	bad_task, good_task, last_solve = load_saved(raw_file)
	first_solve = last_solve
	page = 0
	while True:
		print('Acmp page', page)
		url = 'https://acmp.ru/index.asp?main=status&id_mem={0}&id_res=0&id_t=0&page={1}&uid=0'.format(userId, page)
		r = requests.get(url + str(userId))
		html_parser = BeautifulSoup(r.text, 'html.parser')
		rows = html_parser.find_all('table', {'class' : 'main refresh'})[0].findAll('tr')
		for row in rows:
			id, tim, user, task, lang, res, test, etime, emem = (_.text for _ in row.findAll('td'))
			if first_solve == last_solve:
				first_solve = id
			if id == last_solve:
				rows = []
				break
			task = int(task)
			if res == 'Accepted':
				good_task.append([task, lang])
			else:
				bad_task.append([task, lang])
		if len(rows) < 20:
			break
		page += 1
	dump_saved(raw_file, bad_task, good_task, first_solve)
	return Tasks(bad_task, good_task), len(good_task) + len(bad_task), first_solve


def writable_md(time, data):
	result = '''# Результаты acmp
Здесь можно увидеть результаты решения задач на сайте [acmp](https://acmp.ru). 

## Результаты
Все решенные задачи можно увидеть в `acmp_results.xlsx`.   
Свои результаты можно посмотреть в папке `acmp_results`.  
Домашняя работа написана в папке `tasks`, а её выполнение в папке `tasks_results`.

## Таблица
Время обновления: {}
| ID   | Участник | Место | Рейтинг | Посылки | + (1000) | - (1000) | +    | -    |
| ---- | -------- | ----- | ------- | ------- | -------- | -------- | ---- | ---- |
'''.format(time)
	for x in data:
		result += x[0].writable_md() + x[1].writable_md()
	return result
