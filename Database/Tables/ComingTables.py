from Database.db_base import BaseCategory


class ComingCategory(BaseCategory):
    # Добавьте специфичные для приходов методы и поля, если необходимо

    class Meta:
        db_table = "ComingCategories"