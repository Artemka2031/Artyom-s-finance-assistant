import pandas as pd
from datetime import datetime, timedelta

from Database.Tables.ExpensesTables import Expense


def generate_summary_report(data, timeframe):
    """
    Generates a summary report for expenses or comings aggregated by category and type
    for the specified timeframe: 'day', 'week', 'month'.

    :param data: List of dictionaries containing the operations data.
    :param timeframe: The timeframe for the summary ('day', 'week', 'month').
    :return: A nested dictionary with the structure {Category: {sum, interval: {start, end}, Types: {Type: sum}}}.
    """
    df = pd.DataFrame(data)

    # Преобразование строки даты обратно в объект datetime для фильтрации
    df['date'] = pd.to_datetime(df['date'], format="%d.%m.%y")

    # Определение временного промежутка
    today = pd.Timestamp(datetime.now().date())
    if timeframe == 'day':
        start_date, end_date = today, today
    elif timeframe == 'week':
        start_date = today - pd.Timedelta(days=today.weekday())
        end_date = start_date + pd.Timedelta(days=6)
    elif timeframe == 'month':
        start_date = today.replace(day=1)
        end_date = start_date + pd.offsets.MonthEnd(1)
    else:
        raise ValueError("Invalid timeframe specified. Choose 'day', 'week', or 'month'.")

    # Фильтрация данных по дате
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Агрегация данных
    summary = filtered_df.groupby(['category_name', 'type_name'])['amount'].sum().reset_index(name='total_amount')

    # Структурирование результатов
    result = {}
    for _, row in summary.iterrows():
        category = row['category_name']
        if category not in result:
            result[category] = {'sum': 0, 'interval': {'start': start_date.strftime("%d.%m.%y"),
                                                       'end': end_date.strftime("%d.%m.%y")}, 'Types': {}}
        result[category]['Types'][row['type_name']] = float(row['total_amount'])
        result[category]['sum'] += float(row['total_amount'])

    return result


# Пример использования
expenses_data = Expense.get_all()  # или Coming.get_all() для приходов
timeframe = 'week'  # 'day', 'week', или 'month'
report = generate_summary_report(expenses_data, timeframe)
print(report)


def save_report_to_excel(report, filename="report.xlsx"):
    """
    Saves the given report data to an Excel file.

    :param report: The report data to save. Expected to be a dictionary.
    :param filename: The filename for the Excel file.
    """
    # Создание объекта ExcelWriter для записи в файл
    with pd.ExcelWriter(filename) as writer:
        # Для каждой категории в отчете создаем отдельный лист
        for category, details in report.items():
            # Создаем DataFrame из данных категории
            data = {
                "Type": [],
                "Amount": [],
            }
            for type_name, amount in details['Types'].items():
                data["Type"].append(type_name)
                data["Amount"].append(amount)
            df = pd.DataFrame(data)
            # Запись DataFrame в лист Excel, название листа - название категории
            df.to_excel(writer, sheet_name=category, index=False)


save_report_to_excel(report, "weekly_report.xlsx")
