from datetime import datetime, timedelta

from peewee import Model, IntegrityError, CharField, ForeignKeyField, DateField, JOIN

from Database.db_base import initialize_logger, db, BaseCategory, BaseType
from Database.time_intervals import TimeInterval



class ExpenseCategory(BaseCategory):
    # Добавьте специфичные для расходов методы и поля, если необходимо

    class Meta:
        db_table = "ExpenseCategories"


class ExpenseType(BaseType):
    category = ForeignKeyField(ExpenseCategory)
    category_class = ExpenseCategory
    operation_class = Expense  # Подставьте нужный класс для расходов/приходов

    class Meta:
        database = db
        db_table = "ExpenseTypes"

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

            return new_expense

        except ExpenseCategory.DoesNotExist:
            Expense.logger.warning(f"Ошибка: Категория с ID {category_id} не найдена.")
        except ExpenseType.DoesNotExist:
            Expense.logger.warning(f"Ошибка: Тип с ID {type_id} не найден.")
        except IntegrityError:
            Expense.logger.warning("Ошибка: Проверьте уникальность значения, возможно, такой расход уже существует.")
        except Exception as e:
            Expense.logger.error(f"Ошибка при добавлении расхода: {e}")

    @staticmethod
    def delete_expense(expense_id):
        try:
            expense = Expense.get(Expense.id == expense_id)
            expense.delete_instance()
            Expense.logger.info(f"Расход с ID {expense_id} успешно удален. "
                                f"(Дата: {expense.date}, Категория: {expense.category.name}, Тип: {expense.type.name}, "
                                f"Сумма: {expense.amount}, Комментарий: {expense.comment})")
        except Expense.DoesNotExist:
            Expense.logger.warning(f"Ошибка: Расход с ID {expense_id} не найден.")
            raise Expense.DoesNotExist(f"Ошибка: Расход с ID {expense_id} не найден.")
        except Exception as e:
            Expense.logger.error(f"Ошибка при удалении расхода: {e}")
            raise Exception(f"Ошибка при удалении расхода: {e}")

    @staticmethod
    def get_expenses_in_category_by_time_interval(time_interval: str, category_id: int = None):
        try:
            today = datetime.now().date()

            if time_interval == TimeInterval.TODAY.value:
                start_date = today
            elif time_interval == TimeInterval.LAST_WEEK.value:
                start_date = today - timedelta(days=today.weekday())
            elif time_interval == TimeInterval.CURRENT_MONTH.value:
                start_date = today.replace(day=1)
            else:
                raise ValueError("Неподдерживаемый временной интервал")

            # Преобразуем даты в формат "день.месяц.год"
            formatted_today = today.strftime("%d.%m.%y")
            formatted_start_date = start_date.strftime("%d.%m.%y")

            query = Expense.select(Expense, ExpenseCategory, ExpenseType).join(
                ExpenseCategory, JOIN.INNER, on=(Expense.category == ExpenseCategory.id)
            ).join(
                ExpenseType, JOIN.INNER, on=(Expense.type == ExpenseType.id)
            ).where(
                (Expense.date >= formatted_start_date) & (Expense.date <= formatted_today)
            )

            if category_id is not None:
                query = query.where(Expense.category == category_id)

            expenses = query.execute()

            result_dict = {}
            for expense in expenses:
                category_id = expense.category.id
                type_id = expense.type.id

                if category_id not in result_dict:
                    result_dict[category_id] = {}

                if type_id not in result_dict[category_id]:
                    result_dict[category_id][type_id] = []

                result_dict[category_id][type_id].append({
                    "id": expense.id,
                    "date": expense.date,
                    "amount": expense.amount,
                    "comment": expense.comment,
                })

            return result_dict

        except Exception as e:
            Expense.logger.error(f"Ошибка при получении расходов: {e}")
            return {}

    class Meta:
        database = db
        db_table = "Expenses"
