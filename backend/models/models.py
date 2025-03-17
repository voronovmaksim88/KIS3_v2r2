# models.py

from sqlalchemy import MetaData, Integer, String, ForeignKey, Date, Boolean, Text, DateTime, Table, Column
from sqlalchemy.orm import validates
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped  # используется для аннотации типов столбцов.
from sqlalchemy.orm import mapped_column  # функция для определения столбцов с дополнительными
from sqlalchemy.orm import relationship  # используется для связи таблиц
from typing import Optional, List
from datetime import date
from datetime import datetime

# Переменная, которая хранит информацию о таблицах
metadata = MetaData()


# Класс базы данных. Используется для создания таблиц в базе данных
class Base(DeclarativeBase):
    pass


class Country(Base):
    """Страны"""
    __tablename__ = 'countries'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)


class Manufacturer(Base):
    """Производители, это не конкретное юрлицо это типа брэнд"""
    __tablename__ = 'manufacturers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('countries.id'), nullable=False)

    # Опционально: добавление отношения к Country
    country: Mapped["Country"] = relationship()

    def __repr__(self) -> str:
        return f"Manufacturer(id={self.id}, name={self.name})"


class EquipmentType(Base):
    """Типы оборудования"""
    __tablename__ = 'equipment_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f"EquipmentType(id={self.id}, name={self.name})"


class Currency(Base):
    """Класс "Валюты". Тут просто имена валют"""
    __tablename__ = 'currencies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Currency(id={self.id!r}, name={self.name!r})"


class City(Base):
    """Города"""
    __tablename__ = 'cities'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('countries.id'), nullable=False)

    def __repr__(self) -> str:
        return f"City(id={self.id!r}, name={self.name!r})"


class CounterpartyForm(Base):
    """Формы контрагентов"""
    __tablename__ = 'counterparty_form'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"CounterpartyForm(id={self.id!r}, name={self.name!r})"


class Counterparty(Base):
    """ Контрагенты, юрлица, ИП, ЧЛ и т.д все с кем мы сотрудничаем"""
    __tablename__ = 'counterparty'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
    city_id: Mapped[int | None] = mapped_column(ForeignKey('cities.id'), nullable=True)
    form_id: Mapped[int] = mapped_column(ForeignKey('counterparty_form.id'), nullable=False)
    orders: Mapped[List["Order"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:
        return f"Counterparty(id={self.id!r}, name={self.name!r})"


class Person(Base):
    """Люди - сотрудники, представители заказчиков и т.д."""
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String, nullable=True)  # Отчество
    surname: Mapped[str] = mapped_column(String, nullable=False)  # Фамилия
    phone: Mapped[str | None] = mapped_column(String, nullable=True)  # Телефон
    email: Mapped[str | None] = mapped_column(String, nullable=True)  # Email
    counterparty_id: Mapped[int | None] = mapped_column(ForeignKey('counterparty.id'), nullable=True)
    # Человек может не иметь принадлежности ни к одной компании
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Активен, т.е. если это сотрудник, то с ним можно работать в настоящий момент,
    # если это представитель заказчика, то он жив и ещё работает в нашей сфере
    note: Mapped[str | None] = mapped_column(Text, nullable=True)  # Примечание

    def __repr__(self) -> str:
        return f"Person(id={self.id!r}, name={self.name!r}, surname={self.surname!r})"

    # relations
    developed_boxes = relationship("BoxAccounting", back_populates="scheme_developer",
                                   foreign_keys="[BoxAccounting.scheme_developer_id]")
    assembled_boxes = relationship("BoxAccounting", back_populates="assembler",
                                   foreign_keys="[BoxAccounting.assembler_id]")
    programmed_boxes = relationship("BoxAccounting", back_populates="programmer",
                                    foreign_keys="[BoxAccounting.programmer_id]")
    tested_boxes = relationship("BoxAccounting", back_populates="tester", foreign_keys="[BoxAccounting.tester_id]")


# Вспомогательная таблица для связи многие-ко-многим между Order и Work
order_work = Table(
    'orders_works',
    Base.metadata,
    Column('order_serial', ForeignKey('orders.serial'), primary_key=True),
    Column('work_id', ForeignKey('works.id'), primary_key=True)
)


class Work(Base):
    """Работы, выполняемые по заказам"""
    __tablename__ = 'works'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)  # Название
    description: Mapped[str | None] = mapped_column(String, nullable=True)  # Описание
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Активно, значит эту работу можно назначить новому проекту
    orders: Mapped[List["Order"]] = relationship(secondary="orders_works", back_populates="works")

    def __repr__(self) -> str:
        return f"Work(id={self.id!r}, name={self.name!r})"


class OrderStatus(Base):
    """
    Статусы заказов
    1 = "Не определён"
    2 = "На согласовании"
    3 = "В работе"
    4 = "Просрочено"
    5 = "Выполнено в срок"
    6 = "Выполнено НЕ в срок"
    7 = "Не согласовано"
    8 = "На паузе"
    """
    __tablename__ = 'order_statuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)  # Название
    description: Mapped[str | None] = mapped_column(String, nullable=True)  # Описание
    orders: Mapped[List["Order"]] = relationship(back_populates="status")

    def __repr__(self) -> str:
        return f"OrderStatus(id={self.id!r}, name={self.name!r})"


class Order(Base):
    """Таблица заказов (заявок, проектов)"""
    __tablename__ = 'orders'

    serial: Mapped[str] = mapped_column(String(16), primary_key=True)
    # Серийный номер заказа, формат NNN-MM-YYYY
    # NNN - порядковый номер в этом году
    # MM - месяц создания
    # YYYY - год создания
    name: Mapped[str] = mapped_column(String(64), nullable=False)  # Название
    customer_id: Mapped[int] = mapped_column(ForeignKey('counterparty.id'), nullable=False)  # id заказчика
    customer: Mapped["Counterparty"] = relationship(back_populates="orders")
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Приоритет от 1 до 10
    status_id: Mapped[int] = mapped_column(ForeignKey('order_statuses.id'), nullable=False)  # Статус заказа
    status: Mapped["OrderStatus"] = relationship(back_populates="orders")
    start_moment: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Дата и время создания
    deadline_moment: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Дата и время дедлайна
    end_moment: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Дата и время окончания
    works: Mapped[List["Work"]] = relationship(secondary="orders_works", back_populates="orders")

    """
    Строки ниже нужны для грубой финансовой аналитики
    При создании заказа вписываем сколько надо под него денег заложить на товары, материалы и работы
    Потом в аналитике видно сколько денег в моменте надо под закрытие текущих заказов,
    далее смотрим сколько есть на счёте и делаем выводы
    После того как что-то оплачено из этого полностью, выставляем флаг что оплачено.
    Такой подход не даёт точного анализа расходов, но позволяет быстро определить текущую потребность в деньгах.
    Так жн фиксируем сколько клиент денег должен ещё нам. 
    """
    materials_cost: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Стоимость материалов плановая
    materials_paid: Mapped[bool] = mapped_column(Boolean, default=False)  # Материалы оплачены
    products_cost: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Стоимость материалов плановая
    products_paid: Mapped[bool] = mapped_column(Boolean, default=False)  # Товары оплачены
    work_cost: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Стоимость работ плановая
    work_paid: Mapped[bool] = mapped_column(Boolean, default=False)  # Работы оплачены
    debt: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Задолженность нам
    debt_paid: Mapped[bool] = mapped_column(Boolean, default=False)  # Задолженность оплачена

    @validates('priority')
    def validate_priority(self, key, value):  # noqa
        if value is not None:
            if value < 1 or value > 10:
                raise ValueError("Priority must be between 1 and 10")
        return value

    @validates('status_id')
    def validate_status_id(self, key, value):  # noqa
        if value < 1 or value > 8:
            raise ValueError("Status ID must be between 1 and 8")
        return value

    def __repr__(self) -> str:
        return f"Order(serial={self.serial!r}, name={self.name!r})"

    # relations
    boxes: Mapped[List["BoxAccounting"]] = relationship(back_populates="order")


class BoxAccounting(Base):
    """Таблица учёта шкафов """
    __tablename__ = 'box_accounting'
    serial_num: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)  # Название шкафа
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.serial'), nullable=False)  # Заказ
    scheme_developer_id: Mapped[int] = mapped_column(ForeignKey('people.id'), nullable=False)  # Разработчик схемы
    assembler_id: Mapped[int] = mapped_column(ForeignKey('people.id'), nullable=False)  # Сборщик
    programmer_id: Mapped[int | None] = mapped_column(ForeignKey('people.id'), nullable=True)  # Программист
    tester_id: Mapped[int] = mapped_column(ForeignKey('people.id'), nullable=False)  # Тестировщик

    # Определяем отношения. Пока не знаю зачем
    order = relationship("Order", back_populates="boxes")
    scheme_developer = relationship("Person", foreign_keys="[BoxAccounting.scheme_developer_id]",
                                    back_populates="developed_boxes")
    assembler = relationship("Person", foreign_keys="[BoxAccounting.assembler_id]", back_populates="assembled_boxes")
    programmer = relationship("Person", foreign_keys="[BoxAccounting.programmer_id]", back_populates="programmed_boxes")
    tester = relationship("Person", foreign_keys="[BoxAccounting.tester_id]", back_populates="tested_boxes")


class OrderComment(Base):
    """Таблица комментариев к заказам """
    __tablename__ = 'comments_on_orders'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.serial'), nullable=False)  # Заказ
    moment_of_creation: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now,
                                                                   nullable=True)  # Дата и время публикации комментария
    text: Mapped[str] = mapped_column(Text, nullable=False)  # Текст комментария
    person_id: Mapped[int] = mapped_column(ForeignKey('people.id'), nullable=False)  # Автор комментария


class TaskStatus(Base):
    """
    Статусы задач
    1 = "Не начата"
    2 = "В работе"
    3 = "На паузе"
    4 = "Завершена"
    5 = "Отменена"
    else = "?"
    """
    __tablename__ = 'task_statuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)  # Название статуса задачи

    # Связь с задачами (если будет создана модель Task)
    tasks: Mapped[List["Task"]] = relationship(back_populates="status")

    def __repr__(self) -> str:
        return f"TaskStatus(id={self.id!r}, name={self.name!r})"


class PaymentStatus(Base):
    """
    Статусы оплаты за задачу
    1 = "Нет оплаты", задача не предполагает оплату
    2 = "Возможна", задача в работе если исполнитель сделает её вовремя и качественно, то получит оплату
    3 = "Начислена", задача выполнена оплата начислена
    4 = "Оплачена", задача выполнена и оплачена исполнителю
    else = "?"
    """
    __tablename__ = 'payment_statuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)  # Название статуса оплаты

    # Связь с задачами (если будет создана модель Task)
    tasks: Mapped[List["Task"]] = relationship(back_populates="payment_status")

    def __repr__(self) -> str:
        return f"PaymentStatus(id={self.id!r}, name={self.name!r})"


class Task(Base):
    """
    Задачи
    """
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)


# @add_str_method
# class Task(models.Model):  # Задачи
#     name = models.CharField(null=False, max_length=64, verbose_name="Название")  # Название задачи
#     executor = models.ForeignKey(  # Исполнитель задачи
#         Person,
#         null=True,
#         # Уникальное имя 'related_name' для scheme_developer
#         related_name="task_executor",
#         verbose_name="Исполнитель задачи",
#         on_delete=models.SET_NULL,
#     )
#     planned_duration = models.DurationField(null=True, blank=True)  # Планируемая продолжительность выполнения задачи
#     actual_duration = models.DurationField(null=True, blank=True)  # Фактическая продолжительность выполнения задачи
#     creation_moment = models.DateTimeField(null=True, blank=True)  # Дата и время создания заказа
#     start_moment = models.DateTimeField(null=True, blank=True)  # Дата и время начала выполнения задачи
#     end_moment = models.DateTimeField(null=True, blank=True)  # Дата и время завершения выполнения задачи
#     status = models.ForeignKey(  # Статус выполнения задачи
#         TaskStatus,
#         null=True,
#         on_delete=models.SET_NULL)
#     cost = models.IntegerField(  # Стоимость выполнения задачи, т.е. сколько денег надо заплатить исполнителю, руб
#         null=True,
#         blank=True,
#         verbose_name="Цена задачи",
#     )
#     payment_status = models.ForeignKey(  # Статус оплаты за задачу
#         PaymentStatus,
#         null=True,
#         on_delete=models.SET_NULL)
#     root_task = models.ForeignKey(
#         'self',
#         null=True,
#         related_name='root_tasks',
#         on_delete=models.SET_NULL
#     )
#     parent_task = models.ForeignKey(
#         'self',
#         null=True,
#         related_name='child_tasks',  # Изменено на множественное число
#         on_delete=models.SET_NULL
#     )
#     # child_task = models.ForeignKey(  # Родительская задача
#     #     'self',  # Используем 'self' для ссылки на ту же модель,
#     #     null=True,
#     #     related_name='parent_task',
#     #     on_delete=models.SET_NULL)
#     description = models.TextField(null=True, blank=True)  # Описание задачи
#
#
# '''
# class Equipment_Suppliers(models.Model):  # Поставщик-Оборудование
#     equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE)
#     supplier =
#     - Supplier_ID(компания)
#     - Price_in(наша  входная   цена)
#     - Price_out(выходная   цена, розница)
#     - Link(ссылка)
# '''

# class Equipment(models.Model):  # Класс "Оборудование"
#     name = models.CharField(max_length=32)  # Имя
#     model = models.CharField(max_length=32, blank=True, unique=True)  # Модель
#     vendor_code = models.CharField(
#         max_length=32, blank=True, unique=True)  # Артикул, код поставщика
#     description = models.TextField(blank=True)  # Описание
#     type = models.ForeignKey(
#         EquipmentType, on_delete=models.SET_NULL, null=True)  # Тип
#     manufacturer = models.ForeignKey(
#         Manufacturers, on_delete=models.SET_NULL, null=True)  # Производитель
#     price = models.IntegerField(
#         validators=[MinValueValidator(0), MaxValueValidator(999999)])  # Цена
#     currency = models.ForeignKey(
#         Money, on_delete=models.SET_NULL, null=True)  # Валюта
#     relevance = models.BooleanField(default=True)  # Актуальность
#     price_date = models.DateField()  # Дата обновления цены
#     photo = models.ImageField(upload_to="photos", null=True)
#     objects = models.Manager()
#
#
# class BoxMaterial(models.Model):  # Материалы шкафов
#     name = models.CharField(max_length=16)  # Имя
#     objects = models.Manager()
#
#
# class BoxIp(models.Model):  # Степень защиты корпусов
#     name = models.CharField(max_length=16)  # Имя
#     objects = models.Manager()
#
#
# class Box(models.Model):  # Корпуса шкафов
#     equipment = models.OneToOneField(
#         Equipment, on_delete=models.CASCADE, primary_key=True)
#     # Связь с таблицей оборудования
#     # on_delete = models.CASCADE говорит, что данные текущей модели(UserAccount) будут удаляться в случае удаления
#     # связанного объекта главной модели(User).
#     # primary_key = True указывает, что внешний ключ(через который идет связь с главной моделью) в то же
#     # время будет выступать и в качестве первичного ключа. И создавать отдельное поле для первичного ключа не надо.
#     material = models.ForeignKey(
#         BoxMaterial, on_delete=models.SET_NULL, null=True)  # материал
#     height = models.IntegerField()  # высота
#     width = models.IntegerField()  # ширина
#     depth = models.IntegerField()  # глубина
#     ip = models.ForeignKey(BoxIp, on_delete=models.SET_NULL,
#                            null=True)  # степень защиты
#     objects = models.Manager()
#
