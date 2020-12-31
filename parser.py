import requests
from datetime import datetime
from bs4 import BeautifulSoup


def parse_one(userId):
	url = 'https://acmp.ru/?main=user&id='
	r = requests.get(url + str(userId))
	html_parser = BeautifulSoup(r.text, 'html.parser')
	tasks = html_parser.find_all('p', {'class' : 'text'})[0:2]
	good = [int(x.text) for x in tasks[0] if x.name]
	bad = [int(x.text) for x in tasks[1] if x.name]
	rank =  html_parser.find_all('b', {'class' : 'btext'})[0]
	rank = int(rank.text.split()[1])
	rating = html_parser.find_all('b', {'class' : 'btext'})[1]
	rating = int(rating.text.split()[1])
	userName = html_parser.find_all('td', {'class' : 'menu_title'})[4].text
	userName = bytes(userName, r.encoding).decode('cp1251')
	userName = [s[0].upper() + s[1:].lower() for s in userName.split()]
	userName = ' '.join(userName[0:2])
	return [userId, userName, good, bad, rank, rating]


def writable(parsed):
	result = 'Баллы : ' + str(parsed[5]) + '\n'
	result += 'Место : ' + str(parsed[4]) + '\n'
	result += 'Решенные задачи (' + str(len(parsed[2])) + '): ' + str(parsed[2])[1:-1] + '\n'
	result += 'Нерешенные  задачи (' + str(len(parsed[3])) + '): ' + str(parsed[3])[1:-1] + '\n'
	return result


def writable_markdown_line(parsed):
	result = '| '
	for x in parsed:
		result += str(x) + ' | '
	return result[:-1]


def writable_markdown_text(time_string, parsed):
	result = '''# Результаты acmp
Здесь можно увидеть результаты решения задач на сайте [acmp](https://acmp.ru). 

## Результаты
Результаты всей группы можно увидеть ниже и в `results.txt`.
Свои результаты можно посмотреть в папке `results`.

## Таблица
Время обновления: ''' + time_string + '\n'
	result += '| Участник | +    | -    | Место | Рейтинг |\n'
	result += '| -------- | ---- | ---- | ----- | ------- |\n'
	for x in parsed:
		result += writable_markdown_line(x) + '\n'
	return result
	

def correct(time):
	return '0' + str(time) if time < 10 else str(time)


def get_time():
	now_datetime = datetime.now()
	now_date = now_datetime.date()
	now_time = now_datetime.time()
	result = str(now_date) + ' '
	result += '{0}:{1}:{2}'.format(correct(now_time.hour), correct(now_time.minute), correct(now_time.second))
	return result


def sort_result(result):
	return result[3]


def parse_all():
	with open('users.txt', 'r') as f:
		files = [int(x) for x in f.read().split('\n')]
	result = []
	parsing_time = get_time()
	for now in files:
		parsed = parse_one(now)
		with open('results/' + parsed[1] + '.txt', 'w', encoding='utf-8') as f:
			f.write(writable(parsed))
		result.append([parsed[1], len(parsed[2]), len(parsed[3]), parsed[4], parsed[5]])
	result = sorted(result, key=sort_result)
	with open('results.txt', 'w', encoding='utf-8') as f:
		f.write('Время обновления: ' + parsing_time + '\n')
		f.write('Участник                 +\t-\tМесто\tРейтинг\n')
		for now in result:
			name = now[0]
			while(len(name) < 25):
				name += ' '
			f.write(name + str(now[1]) + '\t' + str(now[2]) + '\t' + str(now[3]) + '\t' + str(now[4]) + '\n')
	with open('README.md', 'w', encoding='utf-8') as f:
		f.write(writable_markdown_text(parsing_time, result))


if __name__ == '__main__':
	parse_all()