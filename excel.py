import xlsxwriter


class ExcelParentWriter:
    def __add_row__(self, worksheet, idx, *args, color=True):
        i = 0
        for arg in args:
            if arg == 1 and color and i:
                worksheet.write(idx, i, None, self.green_style)
            elif arg == -1 and color and i:
                worksheet.write(idx, i, None, self.red_style)
            elif arg != 0 or not color:
                worksheet.write(idx, i, arg)
            i += 1

    def __write__(self, worksheet, data, row_idx=0, cols_cnt=0):
        start = row_idx
        row_idx += 1
        if not cols_cnt and len(data):
            cols_cnt = len(data[0]) - 1
        for row in data:
            self.__add_row__(worksheet, row_idx, *row, color=(row_idx <= 1000))
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


class ExcelWriter(ExcelParentWriter):
    def __gen_sheet__(self, worksheet, data: list):
        head, wr = ['№'], [[i] for i in range(1, 1001)]
        wr.append(['+'])
        wr.append(['-'])
        wr.append(['Место'])
        wr.append(['Рейтинг'])
        for x in data:
            head.append(x[0])
            for i in range(1, 1001):
                if i in x[1]:
                    wr[i - 1].append(1)
                elif i in x[2]:
                    wr[i - 1].append(-1)
                else:
                    wr[i - 1].append(0)
            wr[1000].append(len(x[1]))
            wr[1001].append(len(x[2]))
            wr[1002].append(x[3])
            wr[1003].append(x[4])
        self.__head__(worksheet, *head)
        self.__write__(worksheet, wr)

    def write(self, filename: str, data: list):
        self.__styles__(filename)
        self.__gen_sheet__(self.workbook.add_worksheet('Результаты'), data)
        self.workbook.close()


