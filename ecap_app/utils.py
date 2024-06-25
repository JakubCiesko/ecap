import numpy as np 
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from .models import Expense, Income, Report
from django.contrib.auth.models import User
from typing import List, Callable, Tuple


def calculate_expenses(quantity: np.array, price: np.array) -> float:
    """
    Calculate the dot product of quantities and prices.

    :param quantity: List of quantities of products.
    :param price: List of prices of products.
    :return: The dot product of quantities and prices.
    """
    if len(quantity) == len(price):
        return np.dot(quantity, price)
    return 0 

def parse_and_calculate_expenses(expenses: List[Expense]) -> float:
    """
    Parse expenses and calculate the total expense using quantities and prices.

    :param expenses: List of Expense objects.
    :return: Total calculated expenses.
    """
    quantity = np.array([expense.amount for expense in expenses])
    price = np.array([expense.product.price for expense in expenses])
    return calculate_expenses(quantity, price)

def calculate_total_user_expenses(user: User) -> float:
    """
    Calculate the total expenses for a user.

    :param user: User object.
    :return: Total expenses amount.
    """
    return parse_and_calculate_expenses(Expense.objects.filter(user=user))

def calculate_total_user_income(user: User) -> float:
    """
    Calculate the total income for a user.

    :param user: User object.
    :return: Total income amount.
    """
    incomes = Income.objects.filter(user=user)
    return sum(income.amount for income in incomes)

def calculate_balance(expenses_fn:Callable, incomes_fn:Callable, *args, **kwargs) -> float:
    """
    Calculate the balance by subtracting expenses from income.

    :param expenses_fn: Function to calculate expenses.
    :param incomes_fn: Function to calculate income.
    :return: Calculated balance.
    """
    expenses = expenses_fn(*args, **kwargs)
    incomes = incomes_fn(*args, **kwargs)
    return incomes - expenses

def calculate_total_user_balance(user:User) -> float:
    """
    Calculate the total balance for a user.

    :param user: User object.
    :return: Total balance amount.
    """
    return calculate_balance(calculate_total_user_expenses, calculate_total_user_income, user)

def calculate_user_expense_from_date(user: User, date: str) -> float:
    """
    Calculate the total expenses for a user from a specific date.

    :param user: User object.
    :param date: Start date for expense calculation.
    :return: Total expenses amount from the specified date.
    """
    return parse_and_calculate_expenses(Expense.objects.filter(user=user, date__gte=date))

def calculate_user_income_from_date(user: User, date: str) -> float:
    """
    Calculate the total income for a user from a specific date.

    :param user: User object.
    :param date: Start date for income calculation.
    :return: Total income amount from the specified date.
    """
    return sum(income.amount for income in Income.objects.filter(user=user, date__gte=date))

def calculate_user_expense_to_date(user: User, date: str) -> float:
    """
    Calculate the total expenses for a user up to a specific date.

    :param user: User object.
    :param date: End date for expense calculation.
    :return: Total expenses amount up to the specified date.
    """
    return parse_and_calculate_expenses(Expense.objects.filter(user=user, date__lte=date))

def calculate_user_income_to_date(user: User, date: str) -> float:
    """
    Calculate the total income for a user up to a specific date.

    :param user: User object.
    :param date: End date for income calculation.
    :return: Total income amount up to the specified date.
    """
    return sum(income.amount for income in Income.objects.filter(user=user, date__lte=date))

def calculate_user_balance_from_date(user: User, date: str) -> float:
    """
    Calculate the balance for a user from a specific date.

    :param user: User object.
    :param date: Start date for balance calculation.
    :return: Calculated balance from the specified date.
    """
    return calculate_balance(calculate_user_expense_from_date, 
                             calculate_user_income_from_date, 
                             user=user, 
                             date=date
    )

def calculate_user_balance_to_date(user: User, date: str) -> float:
    """
    Calculate the balance for a user up to a specific date.

    :param user: User object.
    :param date: End date for balance calculation.
    :return: Calculated balance up to the specified date.
    """
    return calculate_balance(calculate_user_expense_to_date, 
                             calculate_user_income_to_date, 
                             user=user, 
                             date=date
    )

def preprocess_date_data(date_data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert dates in the data to ordinal values.

    :param date_data: DataFrame containing date data.
    :return: DataFrame with an additional column for ordinal dates.
    """
    date_data = date_data.sort_values(by="date", ignore_index=True)
    date_data["date_ordinal"] = date_data["date"].apply(lambda x: x.toordinal())
    return date_data 

def train_model(data: pd.DataFrame) -> LinearRegression:
    """
    Train a linear regression model on the given data.

    :param data: DataFrame containing date ordinals and amounts.
    :return: Trained LinearRegression model.
    """
    X = data["date_ordinal"].values.reshape(-1,1)
    y = data["amount"].values
    model = LinearRegression()
    model.fit(X,y)
    return model 

def predict_future_data(model: LinearRegression, start_date: datetime.date, days_to_predict: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Predict future data points using the trained model.

    :param model: Trained LinearRegression model.
    :param start_date: Start date for predictions.
    :param days_to_predict: Number of future days to predict.
    :return: Tuple containing future dates and predicted values.
    """
    future_dates = [start_date + timedelta(days=i) for i in range(days_to_predict)]
    future_dates_strings = [future_date.strftime('%Y-%m-%d') for future_date in future_dates]
    future_dates_ordinal = np.array([date.toordinal() for date in future_dates]).reshape(-1, 1)
    return future_dates_strings, model.predict(future_dates_ordinal)

def extrapolate_data_from_date(data: pd.DataFrame, start_date: datetime.date, days_to_predict: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extrapolate future data points based on historical data.

    :param data: DataFrame containing historical data.
    :param start_date: Start date for predictions.
    :param days_to_predict: Number of future days to predict.
    :return: Tuple containing future dates and predicted values.
    """
    if data.empty:
        return [], []
    data = preprocess_date_data(data)
    model = train_model(data)
    future_dates, predicted_data = predict_future_data(model, start_date, days_to_predict)
    return future_dates, predicted_data

def extrapolate_data(data: pd.DataFrame, days_to_predict: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extrapolate future data points based on historical data.

    :param data: DataFrame containing historical data.
    :param start_date: Start date for predictions.
    :param days_to_predict: Number of future days to predict.
    :return: Tuple containing future dates and predicted values.
    """
    if data.empty:
        return [], []
    data = preprocess_date_data(data)
    model = train_model(data)
    start_date = data["date"][len(data)-1]
    future_dates, predicted_data = predict_future_data(model, start_date, days_to_predict)
    return future_dates, predicted_data


def get_user_expenses_by_date(user:User) -> pd.DataFrame:
    """
    Retrieve the expenses of a user by date.

    This function fetches the expense records of a given user from the database
    and returns them as a pandas DataFrame. Each record includes the date and
    the amount of the expense.

    Parameters:
    user (User): The user whose expenses are to be retrieved.

    Returns:
    pd.DataFrame: A DataFrame containing the user's expenses with columns 'date' and 'amount'.
    """
    return pd.DataFrame(list(Expense.objects.filter(user=user).values("date", "amount"))).sort_values(by="date", ascending=True, ignore_index=True)

def get_user_incomes_by_date(user:User) -> pd.DataFrame:
    """
    Retrieve the incomes of a user by date.

    This function fetches the income records of a given user from the database
    and returns them as a pandas DataFrame. Each record includes the date and
    the amount of the income.

    Parameters:
    user (User): The user whose incomes are to be retrieved.

    Returns:
    pd.DataFrame: A DataFrame containing the user's incomes with columns 'date' and 'amount'.
    """
    return pd.DataFrame(list(Income.objects.filter(user=user).values("date", "amount"))).sort_values(by="date", ascending=True, ignore_index=True)

def extrapolate_user_expenses_from_date(user: User, start_date: datetime.date, days_to_predict: int = 10):
    """
    Extrapolate future expenses for a user.

    :param user: User object.
    :param start_date: Start date for predictions.
    :param days_to_predict: Number of future days to predict.
    :return: Tuple containing future dates and predicted expenses.
    """
    expenses = get_user_expenses_by_date(user)
    return extrapolate_data_from_date(expenses, start_date, days_to_predict)

def extrapolate_user_income_from_date(user: User, start_date: datetime.date, days_to_predict: int = 10):
    """
    Extrapolate future income for a user.

    :param user: User object.
    :param start_date: Start date for predictions.
    :param days_to_predict: Number of future days to predict.
    :return: Tuple containing future dates and predicted income.
    """
    incomes = get_user_incomes_by_date(user)
    return extrapolate_data_from_date(incomes, start_date, days_to_predict)

def extrapolate_user_expenses(user: User, days_to_predict: int = 10):
    """
    Extrapolate future expenses for a user.

    :param user: User object.
    :param days_to_predict: Number of future days to predict.
    :return: Tuple containing future dates and predicted expenses.
    """
    expenses = get_user_expenses_by_date(user)
    return extrapolate_data(expenses, days_to_predict)

def extrapolate_user_income(user: User, days_to_predict: int = 10):
    """
    Extrapolate future income for a user.

    :param user: User object.
    :param days_to_predict: Number of future days to predict.
    :return: Tuple containing future dates and predicted income.
    """
    incomes = get_user_incomes_by_date(user)
    return extrapolate_data(incomes, days_to_predict)

def get_monthly_expense_report(user:User) -> pd.DataFrame:
    """
    Generate a monthly expense report for a user.

    :param user: User object.
    :return: DataFrame with monthly expense totals.
    """
    expenses = Expense.objects.filter(user=user).values("date", "amount")
    df = pd.DataFrame(expenses)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    monthly_report = df.groupby("month")["amount"].sum().reset_index()
    return monthly_report

def calculate_user_balance_over_time(user:User) -> pd.DataFrame:
    """
    Calculate the user's balance over time.

    :param user: User object.
    :return: DataFrame with dates and corresponding balance.
    """
    incomes = pd.DataFrame(list(Income.objects.filter(user=user).values("date", "amount")))
    expenses = pd.DataFrame(list(Expense.objects.filter(user=user).values("date", "amount")))
    if incomes.empty or expenses.empty:
        return pd.DataFrame(columns=["date", "balance"])
    incomes["date"] = pd.to_datetime(incomes["date"])
    expenses["date"] = pd.to_datetime(expenses["date"])
    incomes_by_date = incomes.groupby("date")["amount"].sum().reset_index()
    expense_by_date = expenses.groupby("date")["amount"].sum().reset_index()
    balance_data = pd.DataFrame(
        pd.date_range(  start=min(incomes_by_date["date"].min(), expense_by_date["date"].min()),
                        end=max(incomes_by_date["date"].max(), expense_by_date["date"].max())
        ), 
                        columns=["date"]
    )
    balance_data = balance_data.merge(incomes_by_date, on="date", how="left").rename(columns={"amount": "income"})
    balance_data = balance_data.merge(expense_by_date, on="date", how="left").rename(columns={"amount": "expense"})
    balance_data["income"] = balance_data["income"].fillna(0)
    balance_data["expense"] = balance_data["expense"].fillna(0)
    balance_data["cumulative_income"] = balance_data["income"].cumsum()
    balance_data["cumulative_expense"] = balance_data["expense"].cumsum()
    balance_data["balance"] = balance_data["cumulative_income"].astype(pd.Float64Dtype()) - balance_data["cumulative_expense"].astype(pd.Float64Dtype())
    return balance_data[["date", "balance"]]

def create_report_for_user(user: User, start_date: datetime.date, end_date: datetime.date) -> Report:
    """
    Create a financial report for a user within a specified date range.

    This function generates a report for the given user, covering the specified
    date range from start_date to end_date. It automatically associates the relevant
    expenses and incomes within this period and calculates the total amounts.

    Args:
        user (User): The user for whom the report is to be created.
        start_date (date): The start date of the reporting period.
        end_date (date): The end date of the reporting period.

    Returns:
        Report: The created report instance containing the relevant expenses and incomes.
    """
    report = Report(user=user, start_date=start_date, end_date=end_date)
    report.save()
    report.populate_expenses_and_incomes()
    return report
