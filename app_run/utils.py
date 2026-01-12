from openpyxl import load_workbook, workbook

from geopy.distance import geodesic


def calculate_distance_between_two_positions(start: tuple, end: tuple) -> float:
    '''
    Docstring для calculate_distance_between_two_positions

    :param start_pos: Начальная точка
    :type start_pos: Position
    :param end_pos: Конец точки
    :type end_pos: Position
    :return: Возвращаем дистанцию между двумя точками
    :rtype: float
    '''

    return geodesic(start, end).km


def open_xlsx(xlsx_name: str) -> dict:
    '''
        Функция открытия Excel XLSX таблиц, и последующей валидации их в представлениях
    '''
    wb = load_workbook(xlsx_name)

    ws = wb.active

    result_dict = {}

    # Проходимся циклом по всем столбцам таблицы XLSX, и добавляем его
    # в result_dict в формате {"Название столбца" : ["Все значения этого столбца"]}
    for column in ws.iter_cols(values_only=True):
        header = column[0]
        values = [val for val in column[1:] if val is not None]

        result_dict[header] = values
    
    return result_dict
