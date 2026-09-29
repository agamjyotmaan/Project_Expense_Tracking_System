import mysql.connector
from contextlib import contextmanager
import logging

logger = logging.getLogger('db_helper')

logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('server.log')
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="expense_manager"
    )
    cursor = connection.cursor(dictionary=True)
    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception as e:
        connection.rollback()
        logger.error(f"DB ERROR: {e}")
        raise
    finally:
        cursor.close()
        connection.close()


def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called for {expense_date}")

    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT amount, category, notes FROM expenses WHERE expense_date = %s",
            (expense_date,)
        )
        expenses = cursor.fetchall()
        return expenses


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called for {expense_date}")

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM expenses WHERE expense_date = %s",
            (expense_date,)
        )


def insert_expense(expense_date, amount, category, notes):
    logger.info(f"insert_expense called for {expense_date}, {amount}, {category}, {notes}")

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )


def fetch_data_summary(start_date, end_date):
    logger.info(f"fetch_data_summary called for {start_date} and {end_date}")

    with get_db_cursor() as cursor:
        cursor.execute(
            '''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            GROUP BY category
            ''',
            (start_date, end_date)
        )
        data = cursor.fetchall()
        return data


if __name__ == "__main__":
    expen = fetch_expenses_for_date("2024-08-01")
    print(expen)