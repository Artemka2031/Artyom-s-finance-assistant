from Database.Tables.ComingTables import ComingCategory, ComingType, Coming
from Database.Tables.ExpensesTables import ExpenseCategory, ExpenseType, Expense
from Database.db_base import db


def create_tables_with_drop():
    tables = [ExpenseCategory, ExpenseType, Expense,
              ComingCategory, ComingType, Coming]
    db.connect()
    db.drop_tables(tables, safe=True)  # Добавлено удаление таблиц
    db.create_tables(tables, safe=True)
    db.close()


if __name__ == '__main__':
    create_tables_with_drop()
