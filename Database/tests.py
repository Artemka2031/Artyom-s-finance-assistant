import unittest

from peewee import SqliteDatabase

from create_database import ExpenseCategory, ExpenseType, Expense

test_db = SqliteDatabase(':memory:')


class TestExpenseCategoryMethods(unittest.TestCase):
    def setUp(self):
        print("Начало тестов для ExpenseCategory")
        test_db.bind([ExpenseCategory, ExpenseType], bind_refs=False)
        test_db.connect()
        test_db.create_tables([ExpenseCategory, ExpenseType], safe=True)

    def tearDown(self):
        print("Конец тестов для ExpenseCategory\n")
        test_db.drop_tables([ExpenseCategory, ExpenseType], safe=True)
        test_db.close()

    def test_add_category(self):
        print("Тест: добавление категории")
        ExpenseCategory.add_category("TestCategory")
        categories = ExpenseCategory.get_all_categories()
        self.assertIn("TestCategory", categories)

    def test_get_category_id_by_name(self):
        print("Тест: получение ID категории по имени")
        ExpenseCategory.add_category("TestCategory")
        category_id = ExpenseCategory.get_category_id("TestCategory")
        self.assertIsNotNone(category_id)

    def test_get_category_by_id(self):
        print("Тест: получение категории по ID")
        ExpenseCategory.add_category("TestCategory")
        category_id = ExpenseCategory.get_category_id("TestCategory")
        category_name = ExpenseCategory.get_category_name(category_id)
        self.assertEqual(category_name, "TestCategory")

    def test_get_all_types_from_category(self):
        print("Тест: Получение всех типов расходов в соответствии с категорией")

        # Создаем категории и добавляем в них типы
        category1 = "TestCategory1"
        category2 = "TestCategory2"

        ExpenseCategory.add_category(category1)
        ExpenseCategory.add_category(category2)

        category1_id = ExpenseCategory.get_category_id(category1)
        category2_id = ExpenseCategory.get_category_id(category2)

        ExpenseType.add_expense_type(category1_id, "Type1")
        ExpenseType.add_expense_type(category1_id, "Type2")
        ExpenseType.add_expense_type(category2_id, "Type3")

        # Проверяем, что типы соответствуют категориям
        types_category1 = ExpenseCategory.get_all_types(category1_id)
        self.assertIn("Type1", types_category1)
        self.assertIn("Type2", types_category1)
        self.assertNotIn("Type3", types_category1)

        types_category2 = ExpenseCategory.get_all_types(category2_id)
        self.assertIn("Type3", types_category2)
        self.assertNotIn("Type1", types_category2)
        self.assertNotIn("Type2", types_category2)


class TestExpenseTypeMethods(unittest.TestCase):
    def setUp(self):
        print("Начало тестов для ExpenseType")
        test_db.bind([ExpenseCategory, ExpenseType], bind_refs=False)
        test_db.connect()
        test_db.create_tables([ExpenseCategory, ExpenseType], safe=True)

    def tearDown(self):
        print("Конец тестов для ExpenseType")
        test_db.drop_tables([ExpenseCategory, ExpenseType], safe=True)
        test_db.close()

    def test_add_expense_type(self):
        print("Тест: добавление типа расхода")
        ExpenseCategory.add_category("TestCategory")
        category_id = ExpenseCategory.get_category_id("TestCategory")
        ExpenseType.add_expense_type(category_id, "TestType")
        types = ExpenseCategory.get_all_types(category_id)
        self.assertIn("TestType", types)


class TestExpenseMethods(unittest.TestCase):
    def setUp(self):
        print("Начало тестов для Expense")
        test_db.bind([Expense, ExpenseCategory, ExpenseType], bind_refs=False)
        test_db.connect()
        test_db.create_tables([Expense, ExpenseCategory, ExpenseType], safe=True)

    def tearDown(self):
        print("Конец тестов для Expense")
        test_db.drop_tables([Expense, ExpenseCategory, ExpenseType], safe=True)
        test_db.close()

    def test_add_expense_successful(self):
        print("Тест: успешное добавление расхода")
        category = ExpenseCategory.create(name="TestCategory")
        expense_type = ExpenseType.create(category=category, name="TestType")
        date = "2023-10-21"
        amount = 100
        comment = "За продукты"

        Expense.add_expense(date, category.id, expense_type.id, amount, comment)

        expenses = Expense.select()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].date, date)
        self.assertEqual(expenses[0].category, category)
        self.assertEqual(expenses[0].type, expense_type)
        self.assertEqual(expenses[0].amount, amount)
        self.assertEqual(expenses[0].comment, comment)

    def test_add_expense_missing_category(self):
        print("Тест: попытка добавления расхода с отсутствующей категорией")
        date = "2023-10-21"
        type_id = 1  # ID существующего типа
        amount = "100.00"
        comment = "За продукты"

        with self.assertRaises(ExpenseCategory.DoesNotExist):
            Expense.add_expense(date, 1, type_id, amount, comment)

    def test_add_expense_missing_type(self):
        print("Тест: попытка добавления расхода с отсутствующим типом")
        date = "2023-10-21"
        category_id = 1  # ID существующей категории
        amount = "100.00"
        comment = "За продукты"

        with self.assertRaises(ExpenseType.DoesNotExist):
            Expense.add_expense(date, category_id, 1, amount, comment)


if __name__ == '__main__':
    unittest.main()
