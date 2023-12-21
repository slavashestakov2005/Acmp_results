from excel import AcmpExcelWriter, CodeforcesExcelWriter, ExcelWriter
import os, shutil
import json
import acmp, codeforces
from utils import writable_md_task, get_time


def read_tasks_list(file):
	acmp_ids, cf_ids = [], []
	for ln in file.readlines():
		line = ln.strip()
		if 'acmp' in line.lower():
			acmp_ids.append(int(line.split('.')[0]))
		elif 'codeforces' in line.lower():
			cf_ids.append(line.split(' - ')[1])
		elif line.isdigit():
			acmp_ids.append(int(line))
	return sorted(acmp_ids), sorted(cf_ids)


def delete_folders(*args):
	for folder in args:
		if os.path.exists(folder):
			shutil.rmtree(folder)


def create_folders(*args):
	for folder in args:
		if not os.path.exists(folder):
			os.makedirs(folder)


def parse_group(folder, url_suffix, users, langs):
	raw_acmp, raw_cf = 'raw_acmp/', 'raw_codeforces/'
	tasks_folder, tasks_results = folder + 'tasks/', folder + 'tasks_results/'
	res_acmp, res_cf = folder + 'acmp_results/', folder + 'codeforces_results/'
	delete_folders(tasks_results, res_acmp, res_cf)
	create_folders(raw_acmp, raw_cf, tasks_folder, tasks_results, res_acmp, res_cf)
	acmp_results, cf_results, all_results, parsing_time = [], [], [], get_time()
	for current_user in users:
		name = current_user['name']
		if 'acmp' in current_user:
			acmp_id = current_user['acmp']
			acmp_user = acmp.parse_user_profile(acmp_id)
			acmp_user.set_name(name)
			ac_tasks, acmp_user.send, last_solve = acmp.parse_user_submissions(acmp_id, raw_acmp + str(acmp_id) + '.txt')
			with open(res_acmp + name + '.txt', 'w', encoding='utf-8') as f:
				f.write(acmp_user.writable())
				f.write(ac_tasks.writable(last_solve))
			acmp_results.append([acmp_user, ac_tasks])
		else:
			acmp_id = None
			ac_tasks = acmp.Tasks([], [])
		if 'codeforces' in current_user:
			codeforces_id = current_user['codeforces']
			codeforces_user = codeforces.parse_user_profile(codeforces_id)
			codeforces_user.set_name(name)
			cf_tasks, codeforces_user.send, last_solve = codeforces.parse_user_submissions(codeforces_id, raw_cf + str(codeforces_id) + '.txt')
			with open(res_cf + name + '.txt', 'w', encoding='utf-8') as f:
				f.write(codeforces_user.writable())
				f.write(cf_tasks.writable(last_solve))
			cf_results.append([codeforces_user, cf_tasks])
		else:
			codeforces_id = None
			cf_tasks = codeforces.Tasks([], [])
		all_results.append([name, acmp_id, codeforces_id, ac_tasks, cf_tasks])
	acmp_results = sorted(acmp_results, key=lambda x: x[0].rank)
	AcmpExcelWriter().write(folder + 'acmp_results.xlsx', acmp_results)
	with open(folder + 'acmp_results.md', 'w', encoding='utf-8') as f:
		f.write(acmp.writable_md(parsing_time, acmp_results))

	cf_results = sorted(cf_results, key=lambda x: x[0].rating)
	CodeforcesExcelWriter().write(folder + 'codeforces_results.xlsx', cf_results)
	with open(folder + 'codeforces_results.md', 'w', encoding='utf-8') as f:
		f.write(codeforces.writable_md(parsing_time, cf_results))

	for tasks_file in os.listdir(tasks_folder):
		with open(folder + 'tasks/' + tasks_file, 'r', encoding='utf-8') as f:
			acmp_tasks, cf_tasks = read_tasks_list(f)
		task_full_name = tasks_results + tasks_file.rsplit('.', 1)[0]
		data = ExcelWriter().write(task_full_name + '.xlsx', all_results, acmp_tasks, cf_tasks)
		with open(task_full_name + '.md', 'w', encoding='utf-8') as f:
			f.write(writable_md_task(parsing_time, data, tasks_file.rsplit('.', 1)[0]))


def parse_group_file(filename):
	with open(filename, 'r', encoding='UTF-8') as f:
		data = json.load(f)
	return data['users'], data['langs'], data['url_suffix']


def parse_all():
	main_path = 'groups'
	for group in os.listdir(main_path):
		path = main_path + '/' + group + '/'
		users, langs, url_suffix = parse_group_file(path + 'users.json')
		parse_group(path, url_suffix, users, langs)


if __name__ == '__main__':
	parse_all()
