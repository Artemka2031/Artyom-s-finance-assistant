import logging

from peewee import SqliteDatabase, CharField, Model, IntegrityError, ForeignKeyField

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


class BaseCategory(Model):
    name = CharField(unique=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = initialize_logger(f"{self.__class__.__name__}Logger")

    @classmethod
    def add_category(cls, name: str):
        try:
            new_category = cls.create(name=name)
            cls.logger.info(f"Категория '{new_category.name}' успешно добавлена.")
        except IntegrityError:
            cls.logger.warning(f"Категория с именем '{name}' уже существует в базе данных.")
            raise IntegrityError(f"Категория с именем '{name}' уже существует в базе данных.")

    @classmethod
    def get_all_categories(cls) -> list:
        try:
            categories = cls.select()
            category_list = [{"id": category.id, "name": category.name} for category in categories]
            return category_list
        except Exception as e:
            cls.logger.error(f"Error: {e}")
            return []

    @classmethod
    def get_category_name(cls, category_id: int) -> str | None:
        try:
            category = cls.get(cls.id == category_id)
            return category.name
        except cls.DoesNotExist:
            cls.logger.warning(f"Категория с ID {category_id} не найдена.")
            return None
        except Exception as e:
            cls.logger.error(f"Error: {e}")
            return None

    @classmethod
    def get_category_id(cls, category_name) -> int | None:
        try:
            category = cls.get(cls.name == category_name)
            return category.id
        except cls.DoesNotExist:
            cls.logger.warning(f"Категория с именем '{category_name}' не найдена.")
            return None
        except Exception as e:
            cls.logger.error(f"Error: {e}")
            return None

    class Meta:
        database = db


class BaseType(Model):
    category = ForeignKeyField(BaseCategory)
    name = CharField(unique=False)
    category_class = None  # Добавляем поле для хранения класса категории

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = initialize_logger(f"{self.__class__.__name__}Logger")

    @classmethod
    def get_category_class(cls):
        return cls.category_class

    @classmethod
    def add_type(cls, category_id: int, name: str) -> None:
        try:
            category = cls.get_category_class().get(cls.get_category_class().id == category_id)

            # Проверяем, существует ли тип с таким именем внутри указанной категории
            existing_type = cls.select().where(
                (cls.category == category) &
                (cls.name == name)
            ).first()

            if existing_type:
                cls.logger.warning(f"Тип с именем '{name}' уже существует в категории '{category.name}'.")
                raise IntegrityError(f"Тип с именем '{name}' уже существует в категории '{category.name}'.")
            else:
                new_type = cls.create(category=category, name=name)
                cls.logger.info(f"Успешно добавлен в категорию '{category.name}' тип '{new_type.name}'.")
        except cls.get_category_class().DoesNotExist:
            cls.logger.warning(f"Категория с ID {category_id} не найдена.")
            raise ValueError(f"Категория с ID {category_id} не найдена.")
        except IntegrityError:
            raise IntegrityError(f"Тип с именем '{name}' уже существует в категории '{category.name}'.")
        except Exception as e:
            cls.logger.error(f"Error: {e}")
            raise e

    @classmethod
    def move_type(cls, type_id: int, from_category_id: int, to_category_id: int):
        try:
            # Поиск исходной и целевой категорий
            from_category = cls.get_category_class().get(cls.get_category_class().id == from_category_id)
            to_category = cls.get_category_class().get(cls.get_category_class().id == to_category_id)

            # Поиск и перемещение типа
            expense_type = cls.get(cls.id == type_id)
            expense_type.category = to_category
            expense_type.save()

            cls.logger.info(
                f"Тип '{expense_type.name}' успешно перемещен из категории '{from_category.name}' "
                f"в категорию '{to_category.name}'."
            )
        except cls.DoesNotExist:
            cls.logger.warning(f"Ошибка: Тип с ID {type_id} не найден.")
        except cls.get_category_class().DoesNotExist:
            cls.logger.warning(f"Ошибка: Категория не найдена.")
        except IntegrityError:
            cls.logger.warning("Ошибка: Проверьте уникальность значения, возможно, такой тип уже существует.")
        except Exception as e:
            cls.logger.error(f"Ошибка при перемещении типа: {e}")

    @classmethod
    def get_all_types(cls, category_id: int):
        try:
            types = cls.select().where(cls.category == category_id)
            type_data = [{
                "type_id": type_.id,
                "type_name": type_.name,
                "category_id": type_.category.id,
                "category_name": type_.category.name,
            } for type_ in types]
            return type_data
        except Exception as e:
            cls.logger.error(f"Error: {e}")
            return []

    @classmethod
    def get_type(cls, category_id: int, type_id):
        try:
            # Поиск исходной категории
            category = cls.get_category_class().get(cls.get_category_class().id == category_id)

            # Поиск конкретного типа в данной категории
            expense_type = cls.get((cls.id == type_id) & (cls.category == category))

            return {
                "type_id": expense_type.id,
                "type_name": expense_type.name,
                "category_id": category.id,
                "category_name": category.name
            }
        except cls.DoesNotExist:
            cls.logger.warning(f"Ошибка: Тип с ID {type_id} не найден в данной категории.")
            return None
        except cls.get_category_class().DoesNotExist:
            cls.logger.warning(f"Ошибка: Категория с ID {category_id} не найдена.")
            return None
        except Exception as e:
            cls.logger.error(f"Ошибка при получении информации о типе: {e}")
            return None

    @classmethod
    def rename_type(cls, category_id: int, type_id: int, new_name: str) -> None:
        try:
            old_name = cls.get_type_name(category_id, type_id)
            expense_type = cls.get((cls.id == type_id) & (cls.category_id == category_id))

            # Проверяем, существует ли тип с таким же именем в той же категории
            existing_type = cls.select().where(
                (cls.category == expense_type.category) &
                (cls.name == new_name)
            ).first()

            if existing_type:
                cls.logger.warning(
                    f"Ошибка: Тип с названием '{new_name}' уже существует в категории '{expense_type.category.name}'.")
                raise IntegrityError(
                    f"Ошибка: Тип с названием '{new_name}' уже существует в категории '{expense_type.category.name}'.")
            else:
                expense_type.name = new_name
                expense_type.save()
                cls.logger.info(f"Изменено название типа с '{old_name}' на '{new_name}'")
        except cls.DoesNotExist:
            cls.logger.warning(f"Ошибка: Тип с ID {type_id} и категорией {category_id} не найден.")
        except IntegrityError:
            raise IntegrityError(
                f"Ошибка: Тип с названием '{new_name}' уже существует в категории '{expense_type.category.name}'.")
        except Exception as e:
            cls.logger.error(f"Ошибка при изменении названия типа: {e}")

    @classmethod
    def get_type_name(cls, category_id: int, type_id: int) -> str | None:
        try:
            expense_type = cls.get(cls.id == type_id, cls.category_id == category_id)
            return expense_type.name
        except cls.DoesNotExist:
            cls.logger.warning(f"Категория с ID {type_id} и category_id {category_id} не найдена.")
            return None
        except Exception as e:
            cls.logger.error(f"Error: {e}")
            return None

    class Meta:
        database = db
