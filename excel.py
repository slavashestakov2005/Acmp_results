import xlsxwriter


class ExcelParentWriter:
    def __init__(self):
        self.head_size = 8
    def __add_row__(self, worksheet, idx, *args, color=True):
        i = 0
        for arg in args:
            if idx == 1 and i:
                worksheet.write_url(idx, i, 'https://acmp.ru/?main=user&id={}'.format(arg), self.link_style, str(arg))
            elif i == 0 and type(arg) == int:
                worksheet.write_url(idx, i, 'https://acmp.ru/index.asp?main=task&id_task={}'.format(arg), self.link_style, str(arg))
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
            worksheet.write(cols_cnt - 1, idx, col, self.head_style)
            if widths:
                worksheet.set_column(idx, idx, widths[idx])
            idx += 1
        if not widths:
            worksheet.set_column(0, idx-1, 10)

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


class ExcelWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list, tasks_list=None, lang=None):
        head, wr = ['№'], [['ID'], ['Место'], ['Рейтинг'], ['Посылки'], ['+ (1000)'], ['- (1000)'], ['+'], ['-']]
        if tasks_list is None:
            tasks_list = range(1, max(_[1].max_task for _ in data) + 1)
        else:
            wr, self.head_size = [['ID'], ['+'], ['-']], 3
        tasks_count = max(_[1].max_task for _ in data) + 1
        wr.extend([i] for i in tasks_list)
        for x in data:
            user, tasks = x
            good, bad = 0, 0
            head.append(user.name)
            wr[0].append(user.id)
            if self.head_size == 8:
                wr[1].append(user.rank)
                wr[2].append(user.rating)
                wr[3].append(user.send)
                wr[4].append(tasks.goods)
                wr[5].append(tasks.bads)
                wr[6].append(tasks.goods + tasks.good)
                wr[7].append(tasks.bads + tasks.bad)
            for i in range(len(tasks_list)):
                task = tasks.get_task(tasks_list[i])
                v = 0
                if task.solved(lang) > 0:
                    v = 1
                    good += 1
                elif task.unsolved(lang) > 0:
                    v = -1
                    bad += 1
                wr[i + self.head_size].append([v, task.pm(lang)])
            if self.head_size == 3:
                wr[1].append(good)
                wr[2].append(bad)
        self.__head__(worksheet, *head)
        self.__write__(worksheet, wr)
        if self.head_size == 3:
            return head, wr[0], wr[1], wr[2]

    def write(self, filename: str, data: list, tasks_list=None, lang=None):
        self.__styles__(filename)
        res = self.__gen_sheet__(self.workbook.add_worksheet('Результаты'), data, tasks_list, lang)
        self.workbook.close()
        return res
