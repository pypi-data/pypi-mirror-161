# -*- encoding:utf-8 -*-
import os
import xlsxwriter

from main.settings import STATICFILES_DIRS


class ExcelOperate:
    # 将数据导出为Excel
    @staticmethod
    def write_data_to_excel(save_dir, filename, format, header_list, data_list):
        '''
        瑛式备注
        :param save_dir: 保存文件的目录
        :param filename: 生成文件的文件名
        :param format: 生成文件的文件格式，只能是xlsx,xls,csv
        :param header_list: 文件的表头，即第一行标题
        :return:
        '''

        folder_name = os.path.join(STATICFILES_DIRS[0], save_dir)
        # 没有该目录，则创建
        Jt.make_dir(folder_name=folder_name)

        save_path = os.path.join(STATICFILES_DIRS[0], save_dir + filename + '.' + format)

        # 打开文件
        wb = xlsxwriter.Workbook(save_path)

        # 添加名字为Sheet1的Sheet
        ws = wb.add_worksheet('Sheet1')

        # 设置表头
        row_num = 0
        columns = header_list
        for col_num in range(len(columns)):
            # 表头写入第一行
            ws.write(row_num, col_num, columns[col_num])

        for index, it in enumerate(data_list):
            ws.write(index + 1, 0, it[0])  # A2 写入第A列数据
            ws.write(index + 1, 1, it[1])  # B2 写入第B列数据
            ws.write(index + 1, 2, it[2])  # C2 写入第C列数据
            ws.write(index + 1, 3, it[3])  # D2 写入第D列数据
            ws.write(index + 1, 4, it[4])  # E2 写入第E列数据
            ws.write(index + 1, 5, it[5])  # F2 写入第F列数据
            ws.write(index + 1, 6, it[6])  # G2 写入第G列数据
            ws.write(index + 1, 7, it[7])  # H2 写入第H列数据
            ws.write(index + 1, 8, it[8])  # I2 写入第I列数据
        wb.close()

        return 1







