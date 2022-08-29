import xlsxwriter


class ExcelParentWriter:
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
            self.__add_row__(worksheet, row_idx, *row, color=(row_idx >= 9))
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
    def __gen_sheet__(self, worksheet, data: list):
        tasks_count = max(_[1].max_task for _ in data) + 1
        head, wr = ['№'], [['ID'], ['Место'], ['Рейтинг'], ['Посылки'], ['+ (1000)'], ['- (1000)'], ['+'], ['-']]
        wr.extend([i] for i in range(1, tasks_count))
        for x in data:
            user, tasks = x
            head.append(user.name)
            wr[0].append(user.id)
            wr[1].append(user.rank)
            wr[2].append(user.rating)
            wr[3].append(user.send)
            wr[4].append(tasks.goods)
            wr[5].append(tasks.bads)
            wr[6].append(tasks.goods + tasks.good)
            wr[7].append(tasks.bads + tasks.bad)
            for i in range(1, tasks_count):
                task = tasks.get_task(i)
                v = 0
                if task.good > 0:
                    v = 1
                elif task.bad > 0:
                    v = -1
                wr[i + 7].append([v, task.pm()])
        self.__head__(worksheet, *head)
        self.__write__(worksheet, wr)

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Результаты'), data)
        self.workbook.close()
