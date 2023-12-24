import xlsxwriter
import re

'''
    s - solve
    d - simple text (data)
    a - acmp
    c - codeforces
    t - task
    u - user
'''

class ExcelParentWriter:
    def __format_url(self, url: str, *data):
        if data is None:
            return ''
        return url.format(*data)

    def user_cf_url(self, user_id):
        return self.__format_url('https://codeforces.com/profile/{}', user_id)

    def task_cf_url(self, task_id):
        try:
            parse = re.findall(r'(\d+)\s*(\D+)', task_id)[0]
            return self.__format_url('https://codeforces.com/contest/{}/problem/{}', *parse)
        except Exception:
            return ''

    def user_acmp_url(self, user_id):
        return self.__format_url('https://acmp.ru/?main=user&id={}', user_id)

    def task_acmp_url(self, task_id):
        return self.__format_url('https://acmp.ru/index.asp?main=task&id_task={}', task_id)

    def __add_row__(self, worksheet, idx, *args, color=True):
        i = 0
        for val in args:
            t, arg = val[0], val[1]
            if 'a' in t or 'c' in t:
                url = None
                if t == 'at':
                    url = self.task_acmp_url(arg)
                elif t == 'au':
                    url = self.user_acmp_url(arg)
                elif t == 'ct':
                    url = self.task_cf_url(arg)
                elif t == 'cu':
                    url = self.user_cf_url(arg)
                worksheet.write_url(idx, i, url, self.link_style, str(arg or ''))
            elif type(arg) == list and arg[0] == 1 and color and i:
                worksheet.write(idx, i, arg[1], self.green_style)
            elif type(arg) == list and arg[0] == -1 and color and i:
                worksheet.write(idx, i, arg[1], self.red_style)
            elif arg != 0 or not color:
                worksheet.write(idx, i, arg if type(arg) != list else None)
            i += 1

    def __write__(self, worksheet, data, row_idx=0, cols_cnt=0):
        start = row_idx
        row_idx += 1
        if not cols_cnt and len(data):
            cols_cnt = len(data[0]) - 1
        for row in data:
            self.__add_row__(worksheet, row_idx, *row, color=(row_idx >= self.head_size + 1))
            row_idx += 1
        worksheet.autofilter(start, 0, row_idx-1, cols_cnt)

    def __head__(self, worksheet, *cols, title=None, widths=None):
        cols_cnt = 1 if not title else 3
        worksheet.freeze_panes(cols_cnt, 0)
        if title:
            worksheet.merge_range('A1:{}1'.format(chr(ord('A') + len(cols) - 1)), title, self.caps_style)
        idx = 0
        for col in cols:
            t, val = col[0], col[1]
            worksheet.write(cols_cnt - 1, idx, val, self.head_style)
            if widths:
                worksheet.set_column(idx, idx, widths[idx])
            idx += 1
        if not widths:
            worksheet.set_column(0, idx - 1, 10)

    def __footer__(self, worksheet, cols: list, widths: list, styles: list, row: int):
        while len(widths) < len(cols):
            widths.append(1)
        while len(styles) < len(cols):
            styles.append(self.normal_style)
        col = 0
        for i in range(len(cols)):
            if widths[i] > 1:
                worksheet.merge_range('{1}{0}:{2}{0}'.format(row + 1, chr(ord('A') + col),
                                                             chr(ord('A') + col + widths[i] - 1)), cols[i], styles[i])
            else:
                worksheet.write(row, col, cols[i], styles[i])
            col += widths[i]

    def __styles__(self, filename: str):
        self.workbook = xlsxwriter.Workbook(filename)
        self.head_style = self.workbook.add_format({'bold': True, 'text_wrap': True, 'align': 'center'})
        self.head_style.set_font_size(14)
        self.green_style = self.workbook.add_format({'bg_color': 'green'})
        self.red_style = self.workbook.add_format({'bg_color': 'red'})
        self.link_style = self.workbook.add_format({'color': 'blue'})
        self.link_style.set_underline()


class AcmpExcelWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list):
        lang = None
        head, wr = [('d', '№')], [[('d', 'ID')], [('d', 'Место')], [('d', 'Рейтинг')], [('d', 'Посылки')], [('d', '+ (1000)')], [('d', '- (1000)')], [('d', '+')], [('d', '-')]]
        self.head_size = 8
        tasks_list = range(1, max(_[1].max_task for _ in data) + 1)
        wr.extend([('at', i)] for i in tasks_list)
        for x in data:
            user, tasks = x
            good, bad = 0, 0
            head.append(('d', user.name))
            wr[0].append(('au', user.id))
            if self.head_size == 8:
                wr[1].append(('d', user.rank))
                wr[2].append(('d', user.rating))
                wr[3].append(('d', user.send))
                wr[4].append(('d', tasks.goods))
                wr[5].append(('d', tasks.bads))
                wr[6].append(('d', tasks.goods + tasks.good))
                wr[7].append(('d', tasks.bads + tasks.bad))
            for i in range(len(tasks_list)):
                task = tasks.get_task(tasks_list[i])
                v = 0
                if task.solved(lang) > 0:
                    v = 1
                    good += 1
                elif task.unsolved(lang) > 0:
                    v = -1
                    bad += 1
                wr[i + self.head_size].append(('s', [v, task.pm(lang)]))
            if self.head_size == 3:
                wr[1].append(('d', good))
                wr[2].append(('d', bad))
        self.__head__(worksheet, *head)
        self.__write__(worksheet, wr)
        if self.head_size == 3:
            return head, wr[0], wr[1], wr[2]

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        res = self.__gen_sheet__(self.workbook.add_worksheet('Результаты'), data)
        self.workbook.close()
        return res


class CodeforcesExcelWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list):
        lang = None
        head, wr = [('d', '№')], [[('d', 'Хендл')], [('d', 'Рейтинг')], [('d', 'Посылки')], [('d', '+')], [('d', '-')]]
        self.head_size = 5
        tasks_list = set()
        for user in data:
            for task in user[1].tasks:
                tasks_list.add(task.id)
        tasks_list = sorted(tasks_list)
        wr.extend([('ct', str(i[0]) + i[1])] for i in tasks_list)
        for x in data:
            user, tasks = x
            good, bad = 0, 0
            head.append(('d', user.name))
            wr[0].append(('cu', user.handle))
            if self.head_size == 5:
                wr[1].append(('d', user.rating))
                wr[2].append(('d', user.send))
                wr[3].append(('d', tasks.good))
                wr[4].append(('d', tasks.bad))
            for i in range(len(tasks_list)):
                task = tasks.get_task(tasks_list[i])
                v = 0
                if task.solved(lang) > 0:
                    v = 1
                    good += 1
                elif task.unsolved(lang) > 0:
                    v = -1
                    bad += 1
                wr[i + self.head_size].append(('s', [v, task.pm(lang)]))
            if self.head_size == 3:
                wr[1].append(('d', good))
                wr[2].append(('d', bad))
        self.__head__(worksheet, *head)
        self.__write__(worksheet, wr)
        if self.head_size == 3:
            return head, wr[0], wr[1], wr[2]

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        res = self.__gen_sheet__(self.workbook.add_worksheet('Результаты'), data)
        self.workbook.close()
        return res


class ExcelWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, all_res: list, acmp_task: list, cf_task: list):
        lang = None
        head, wr = [('d', '№')], [[('d', 'Acmp')], [('d', 'Codeforces')], [('d', '+')], [('d', '-')]]
        self.head_size = 4
        wr.extend([('at', i)] for i in acmp_task)
        wr.extend([('ct', i)] for i in cf_task)
        for x in all_res:
            name, acmp_id, codeforces_id, ac_tasks, cf_tasks = x
            good, bad = 0, 0
            head.append(('d', name))
            wr[0].append(('au', acmp_id))
            wr[1].append(('cu', codeforces_id))
            for i in range(len(acmp_task)):
                task = ac_tasks.get_task(acmp_task[i])
                v = 0
                if task.solved(lang) > 0:
                    v = 1
                    good += 1
                elif task.unsolved(lang) > 0:
                    v = -1
                    bad += 1
                wr[i + self.head_size].append(('s', [v, task.pm(lang)]))
            for i in range(len(cf_task)):
                task = cf_tasks.get_task(cf_task[i])
                v = 0
                if task.solved(lang) > 0:
                    v = 1
                    good += 1
                elif task.unsolved(lang) > 0:
                    v = -1
                    bad += 1
                wr[i + len(acmp_task) + self.head_size].append(('s', [v, task.pm(lang)]))
            wr[2].append(('d', good))
            wr[3].append(('d', bad))
        self.__head__(worksheet, *head)
        self.__write__(worksheet, wr)
        return head, wr[0], wr[1], wr[2], wr[3]

    def write(self, filename: str, all_res: list, acmp_tasks: list, cf_tasks: list):
        self.__styles__(filename)
        res = self.__gen_sheet__(self.workbook.add_worksheet('Результаты'), all_res, acmp_tasks, cf_tasks)
        self.workbook.close()
        return res
