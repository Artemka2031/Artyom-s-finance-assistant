from Database.Tables.ComingTables import ComingCategory
from Database.Tables.ExpensesTables import ExpenseCategory, ExpenseType, Expense
from Database.db_base import db


def create_tables_if_not_exist():
    tables = [ExpenseCategory, ExpenseType, Expense,
              ComingCategory]
    db.connect()
    db.create_tables(tables, safe=True)
    db.close()


if __name__ == '__main__':
    create_tables_if_not_exist()
