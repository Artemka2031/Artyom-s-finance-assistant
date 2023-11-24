import logging
from datetime import timedelta, datetime

from peewee import Model, CharField, DateField, ForeignKeyField, SqliteDatabase, IntegrityError
from Path import dbPath

# Создайте подключение к базе данных (SQLite в этом случае)
db = SqliteDatabase(dbPath)


def initialize_logger(logger_name, log_level=logging.INFO):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(log_level)

    return logger


# Определите модель для таблицы Category
class ExpenseCategory(Model):
    name = CharField(unique=True)

    logger = initialize_logger("ExpenseCategory")

    @staticmethod
    def add_category(name: str):
        try:
            new_category = ExpenseCategory.create(name=name)
            ExpenseCategory.logger.info(f"Категория '{new_category.name}' успешно добавлена.")
        except IntegrityError:
            ExpenseCategory.logger.warning(f"Категория с именем '{name}' уже существует в базе данных.")
            raise IntegrityError(f"Категория с именем '{name}' уже существует в базе данных.")

    @staticmethod
    def change_category_name(category_id: int, new_name: str) -> None:
        try:
            category = ExpenseCategory.get(ExpenseCategory.id == category_id)
            category.name = new_name
            category.save()
            ExpenseCategory.logger.info(f"Изменено название категории с ID {category_id} на '{new_name}'")
        except ExpenseCategory.DoesNotExist:
            ExpenseCategory.logger.warning(f"Ошибка: Категория с ID {category_id} не найдена.")
        except IntegrityError:
            ExpenseCategory.logger.warning(f"Ошибка: Категория с названием '{new_name}' уже существует в базе данных.")
        except Exception as e:
            ExpenseCategory.logger.error(f"Ошибка при изменении названия категории: {e}")

    @staticmethod
    def delete_category(category_id: int) -> None:
        try:
            # Поиск и удаление категории
            category = ExpenseCategory.get(ExpenseCategory.id == category_id)

            # Удаление всех связанных типов в таблице ExpenseType
            types = ExpenseType.select().where(ExpenseType.category == category_id)
            for expense_type in types:
                ExpenseType.delete_type(expense_type.id)  # Используем метод delete_type для удаления типов

            # Удаление категории
            ExpenseCategory.logger.info(f"Категория с ID {category_id} успешно удалена: {category.name}")
            category.delete_instance()

        except ExpenseCategory.DoesNotExist:
            ExpenseCategory.logger.warning(f"Ошибка: Категория с ID {category_id} не найдена.")
        except IntegrityError:
            ExpenseCategory.logger.warning(
                "Ошибка: Проверьте уникальность значения, возможно, такая категория уже существует.")
        except Exception as e:
            ExpenseCategory.logger.error(f"Ошибка при удалении категории: {e}")

    @staticmethod
    def get_all_categories() -> list:
        try:
            categories = ExpenseCategory.select()
            category_list = [{"id": category.id, "name": category.name} for category in categories]
            return category_list
        except Exception as e:
            ExpenseCategory.logger.error(f"Error: {e}")
            return []

    @staticmethod
    def get_category_name(category_id: int) -> str | None:
        try:
            category = ExpenseCategory.get(ExpenseCategory.id == category_id)
            return category.name
        except ExpenseCategory.DoesNotExist:
            ExpenseCategory.logger.warning(f"Категория с ID {category_id} не найдена.")
            return None
        except Exception as e:
            ExpenseCategory.logger.error(f"Error: {e}")
            return None

    @staticmethod
    def get_category_id(category_name) -> int | None:
        try:
            category = ExpenseCategory.get(ExpenseCategory.name == category_name)
            return category.id
        except ExpenseCategory.DoesNotExist:
            ExpenseCategory.logger.warning(f"Категория с именем '{category_name}' не найдена.")
            return None
        except Exception as e:
            ExpenseCategory.logger.error(f"Error: {e}")
            return None

    @staticmethod
    def get_all_types(category_id: int) -> list:
        try:
            types = ExpenseType.select().where(ExpenseType.category == category_id)
            return [expense_type.name for expense_type in types]
        except Exception as e:
            ExpenseCategory.logger.error(f"Error: {e}")
            return []

    @staticmethod
    def get_all_types_by_name(category_name: str) -> list:
        category_id = ExpenseCategory.get_category_id(category_name)
        if category_id is not None:
            return ExpenseCategory.get_all_types(category_id)
        return []

    class Meta:
        database = db
        db_table = "Categories"


# Определите модель для таблицы Type
class ExpenseType(Model):
    category = ForeignKeyField(ExpenseCategory)
    name = CharField(unique=False)

    logger = initialize_logger("ExpenseType")

    @staticmethod
    def add_expense_type(category_id: int, name: str) -> None:
        try:
            category = ExpenseCategory.get(ExpenseCategory.id == category_id)

            # Проверяем, существует ли тип с таким именем внутри указанной категории
            existing_type = ExpenseType.select().where(
                (ExpenseType.category == category) &
                (ExpenseType.name == name)
            ).first()

            if existing_type:
                ExpenseType.logger.warning(f"Тип с именем '{name}' уже существует в категории '{category.name}'.")
                raise IntegrityError(f"Тип с именем '{name}' уже существует в категории '{category.name}'.")
            else:
                new_type = ExpenseType.create(category=category, name=name)
                ExpenseType.logger.info(f"Успешно добавлен в категорию '{category.name}' тип '{new_type.name}'.")
        except ExpenseCategory.DoesNotExist:
            ExpenseType.logger.warning(f"Категория с ID {category_id} не найдена.")
            raise ValueError(f"Категория с ID {category_id} не найдена.")
        except IntegrityError:
            raise IntegrityError(f"Тип с именем '{name}' уже существует в категории '{category.name}'.")
        except Exception as e:
            ExpenseType.logger.error(f"Error: {e}")
            raise e

    @staticmethod
    def move_type(type_id: int, from_category_id: int, to_category_id: int):
        try:
            # Поиск исходной и целевой категорий
            from_category = ExpenseCategory.get(ExpenseCategory.id == from_category_id)
            to_category = ExpenseCategory.get(ExpenseCategory.id == to_category_id)

            # Поиск и перемещение типа расхода
            expense_type = ExpenseType.get(ExpenseType.id == type_id)
            expense_type.category = to_category
            expense_type.save()

            ExpenseType.logger.info(
                f"Тип расхода '{expense_type.name}' успешно перемещен из категории '{from_category.name}' "
                f"в категорию '{to_category.name}'."
            )
        except ExpenseType.DoesNotExist:
            ExpenseType.logger.warning(f"Ошибка: Тип с ID {type_id} не найден.")
        except ExpenseCategory.DoesNotExist:
            ExpenseType.logger.warning(f"Ошибка: Категория не найдена.")
        except IntegrityError:
            ExpenseType.logger.warning("Ошибка: Проверьте уникальность значения, возможно, такой тип уже существует.")
        except Exception as e:
            ExpenseType.logger.error(f"Ошибка при перемещении типа: {e}")

    @staticmethod
    def get_all_types(category_id: int):
        try:
            types = ExpenseType.select().where(ExpenseType.category == category_id)
            type_data = [{
                "type_id": type_.id,
                "type_name": type_.name,
                "category_id": type_.category.id,
                "category_name": type_.category.name,
            } for type_ in types]
            return type_data
        except Exception as e:
            ExpenseType.logger.error(f"Error: {e}")
            return []

    @staticmethod
    def get_type(category_id: int, type_id):
        try:
            # Поиск исходной категории
            category = ExpenseCategory.get(ExpenseCategory.id == category_id)

            # Поиск конкретного типа расхода в данной категории
            expense_type = ExpenseType.get((ExpenseType.id == type_id) & (ExpenseType.category == category))

            return {
                "type_id": expense_type.id,
                "type_name": expense_type.name,
                "category_id": category.id,
                "category_name": category.name
            }
        except ExpenseType.DoesNotExist:
            ExpenseType.logger.warning(f"Ошибка: Тип расхода с ID {type_id} не найден в данной категории.")
            return None
        except ExpenseCategory.DoesNotExist:
            ExpenseType.logger.warning(f"Ошибка: Категория с ID {category_id} не найдена.")
            return None
        except Exception as e:
            ExpenseType.logger.error(f"Ошибка при получении информации о типе расхода: {e}")
            return None

    @staticmethod
    def rename_type(category_id: int, type_id: int, new_name: str) -> None:
        try:
            old_name = ExpenseType.get_type_name(category_id, type_id)
            expense_type = ExpenseType.get((ExpenseType.id == type_id) & (ExpenseType.category_id == category_id))

            # Проверяем, существует ли тип с таким же именем в той же категории
            existing_type = ExpenseType.select().where(
                (ExpenseType.category == expense_type.category) &
                (ExpenseType.name == new_name)
            ).first()

            if existing_type:
                ExpenseType.logger.warning(
                    f"Ошибка: Тип с названием '{new_name}' уже существует в категории '{expense_type.category.name}'.")
                raise IntegrityError(
                    f"Ошибка: Тип с названием '{new_name}' уже существует в категории '{expense_type.category.name}'.")
            else:
                expense_type.name = new_name
                expense_type.save()
                ExpenseType.logger.info(f"Изменено название типа с '{old_name}' на '{new_name}'")
        except ExpenseType.DoesNotExist:
            ExpenseType.logger.warning(f"Ошибка: Тип с ID {type_id} и категорией {category_id} не найден.")
        except IntegrityError:
            raise IntegrityError(
                f"Ошибка: Тип с названием '{new_name}' уже существует в категории '{expense_type.category.name}'.")
        except Exception as e:
            ExpenseType.logger.error(f"Ошибка при изменении названия типа: {e}")

    @staticmethod
    def get_type_name(category_id: int, type_id: int, ) -> str | None:
        try:
            expense_type = ExpenseType.get(ExpenseType.id == type_id, ExpenseType.category_id == category_id)
            return expense_type.name
        except ExpenseType.DoesNotExist:
            ExpenseType.logger.warning(f"Категория с ID {type_id} и category_id {category_id} не найдена.")
            return None
        except Exception as e:
            ExpenseType.logger.error(f"Error: {e}")
            return None

    @staticmethod
    def delete_type(type_id: int) -> None:
        try:
            # Поиск и удаление типа
            expense_type = ExpenseType.get(ExpenseType.id == type_id)

            # Удаление всех расходов, связанных с этим типом
            expenses = Expense.select().where(Expense.type == type_id)
            for expense in expenses:
                Expense.delete_expense_by_id(expense.id)

            # Удаление типа
            ExpenseType.logger.info(
                f"Тип с ID {type_id} успешно удален из категории '{expense_type.category.name}': {expense_type.name}")
            expense_type.delete_instance()

        except ExpenseType.DoesNotExist:
            ExpenseType.logger.warning(f"Ошибка: Тип с ID {type_id} не найден.")
        except IntegrityError:
            ExpenseType.logger.warning("Ошибка: Проверьте уникальность значения, возможно, такой тип уже существует.")
        except Exception as e:
            ExpenseType.logger.error(f"Ошибка при удалении типа: {e}")

    class Meta:
        database = db
        db_table = "Types"


# Определите модель для таблицы Expense
class Expense(Model):
    date = DateField()
    category = ForeignKeyField(ExpenseCategory)
    type = ForeignKeyField(ExpenseType)
    amount = CharField()
    comment = CharField()

    logger = initialize_logger("Expense")

    @staticmethod
    def get_all_expenses():
        try:
            expenses = Expense.select()
            expense_list = []
            for expense in expenses:
                expense_dict = {
                    "id": expense.id,
                    "date": expense.date,
                    "category": expense.category.name,
                    "type": expense.type.name,
                    "amount": expense.amount,
                    "comment": expense.comment
                }
                expense_list.append(expense_dict)
            return expense_list
        except Exception as e:
            Expense.logger.error(f"Ошибка при получении всех расходов: {e}")
            return []

    @staticmethod
    def add_expense(date, category_id, type_id, amount, comment):
        try:
            category = ExpenseCategory.get(ExpenseCategory.id == category_id)
            expense_type = ExpenseType.get(ExpenseType.id == type_id)
            new_expense = Expense.create(date=date, category=category, type=expense_type, amount=amount,
                                         comment=comment)
            Expense.logger.info(
                f"В категорию '{category.name}' добавлен новый расход (ID: {new_expense.id}, Дата: {date}, "
                f"Тип: {expense_type.name}, Сумма: {amount}, Комментарий: {comment})")

        except ExpenseCategory.DoesNotExist:
            Expense.logger.warning(f"Ошибка: Категория с ID {category_id} не найдена.")
        except ExpenseType.DoesNotExist:
            Expense.logger.warning(f"Ошибка: Тип с ID {type_id} не найден.")
        except IntegrityError:
            Expense.logger.warning("Ошибка: Проверьте уникальность значения, возможно, такой расход уже существует.")
        except Exception as e:
            Expense.logger.error(f"Ошибка при добавлении расхода: {e}")

    @staticmethod
    def delete_expense_by_id(expense_id):
        try:
            expense = Expense.get(Expense.id == expense_id)
            expense.delete_instance()
            Expense.logger.info(f"Расход с ID {expense_id} успешно удален. "
                                f"(Дата: {expense.date}, Категория: {expense.category.name}, Тип: {expense.type.name}, "
                                f"Сумма: {expense.amount}, Комментарий: {expense.comment})")
        except Expense.DoesNotExist:
            Expense.logger.warning(f"Ошибка: Расход с ID {expense_id} не найден.")
        except Exception as e:
            Expense.logger.error(f"Ошибка при удалении расхода: {e}")

    @staticmethod
    def get_expenses_today():
        try:
            # Получение текущей даты
            today = datetime.now().date()

            # Запрос на получение расходов за сегодня
            expenses_today = Expense.select().where(Expense.date == today)

            # Формирование словаря с расходами по категориям и типам
            result_dict = {}
            for expense in expenses_today:
                category_id = expense.category.id
                type_id = expense.type.id

                # Создание вложенного словаря для типа, если его еще нет
                if category_id not in result_dict:
                    result_dict[category_id] = {}

                if type_id not in result_dict[category_id]:
                    result_dict[category_id][type_id] = []

                # Добавление расхода в список
                result_dict[category_id][type_id].append({
                    "id": expense.id,
                    "date": expense.date,
                    "amount": expense.amount,
                    "comment": expense.comment,
                })

            return result_dict

        except Exception as e:
            Expense.logger.error(f"Ошибка при получении расходов за сегодня: {e}")
            return {}

    @staticmethod
    def get_expenses_last_week():
        try:
            # Получение текущей даты
            today = datetime.now().date()

            # Вычисление начала текущей недели (Понедельник)
            start_of_week = today - timedelta(days=today.weekday())

            # Запрос на получение расходов за последнюю неделю
            expenses_last_week = Expense.select().where((Expense.date >= start_of_week) & (Expense.date <= today))

            # Формирование словаря с расходами по категориям и типам
            result_dict = {}
            for expense in expenses_last_week:
                category_id = expense.category.id
                type_id = expense.type.id

                # Создание вложенного словаря для типа, если его еще нет
                if category_id not in result_dict:
                    result_dict[category_id] = {}

                if type_id not in result_dict[category_id]:
                    result_dict[category_id][type_id] = []

                # Добавление расхода в список
                result_dict[category_id][type_id].append({
                    "id": expense.id,
                    "date": expense.date,
                    "amount": expense.amount,
                    "comment": expense.comment,
                })

            return result_dict

        except Exception as e:
            Expense.logger.error(f"Ошибка при получении расходов за последнюю неделю: {e}")
            return {}

    @staticmethod
    def get_expenses_current_month():
        try:
            # Получение текущей даты
            today = datetime.now().date()

            # Получение первого дня текущего месяца
            first_day_of_month = today.replace(day=1)

            # Запрос на получение расходов за текущий месяц
            expenses_current_month = Expense.select().where(
                (Expense.date >= first_day_of_month) & (Expense.date <= today)
            )

            # Формирование словаря с расходами по категориям и типам
            result_dict = {}
            for expense in expenses_current_month:
                category_id = expense.category.id
                type_id = expense.type.id

                # Создание вложенного словаря для типа, если его еще нет
                if category_id not in result_dict:
                    result_dict[category_id] = {}

                if type_id not in result_dict[category_id]:
                    result_dict[category_id][type_id] = []

                # Добавление расхода в список
                result_dict[category_id][type_id].append({
                    "id": expense.id,
                    "date": expense.date,
                    "amount": expense.amount,
                    "comment": expense.comment,
                })

            return result_dict

        except Exception as e:
            Expense.logger.error(f"Ошибка при получении расходов за текущий месяц: {e}")
            return {}

    class Meta:
        database = db
        db_table = "Expenses"


def create_tables_if_not_exist():
    tables = [ExpenseCategory, ExpenseType, Expense]
    db.connect()
    db.create_tables(tables, safe=True)
    db.close()


if __name__ == '__main__':
    # pass
    create_tables_if_not_exist()
