import numpy as np 
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from .models import Expense, Income, Report, SavingGoal, Friend
from django.contrib.auth.models import User
from django.db.models import Max, Min, Avg, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpRequest
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
    price = np.array([1 for _ in expenses])#np.array([expense.product.price for expense in expenses])
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
    expenses = float(expenses_fn(*args, **kwargs))
    incomes = float(incomes_fn(*args, **kwargs))
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
    if len(X) > 1:
        model = LinearRegression()
        model.fit(X,y)
        return model
    return None

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
    if model:
        return future_dates_strings, model.predict(future_dates_ordinal)
    return future_dates_strings, [0]*len(future_dates_strings)

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
    try: 
        return pd.DataFrame(list(Expense.objects.filter(user=user).values("date", "amount"))).sort_values(by="date", ascending=True, ignore_index=True)
    except KeyError:
        return pd.DataFrame([], columns=["date", "amount"])

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
    try: 
        return pd.DataFrame(list(Income.objects.filter(user=user).values("date", "amount"))).sort_values(by="date", ascending=True, ignore_index=True)
    except KeyError:
        return pd.DataFrame([], columns=["date", "amount"])

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
    report.save()
    return report

def get_categories(transfers) -> dict:
    try: #TODO: REMOVE .product.price as it is no longer a possible attribute of any model
        extract_data = lambda transfer: (transfer.category, transfer.amount * transfer.product.price)
        transfers = pd.DataFrame([extract_data(transfer) for transfer in transfers], columns=["category", "amount"])
    except AttributeError:
        extract_data = lambda transfer: (transfer.category, float(transfer.amount))
        transfers = transfers = pd.DataFrame([extract_data(transfer) for transfer in transfers], columns=["category", "amount"])
    transfers_by_category = transfers.groupby(by="category").sum()
    total_transfer = transfers["amount"].sum()
    transfers_by_category["percentage"] = transfers_by_category / total_transfer
    return transfers_by_category.to_dict()

def get_user_expense_categories(user:User) -> dict:
    expenses = Expense.objects.filter(user=user)
    return get_categories(expenses)

def get_user_income_categories(user: User) -> dict:
    incomes = Income.objects.filter(user=user)
    return get_categories(incomes)

def get_saving_goal(user: User) -> dict: 
    SavingGoal.objects.exists()
    saving_goal = SavingGoal.objects.filter(user=user).first()
    return {"current": saving_goal.current_amount, "goal": saving_goal.target_amount, "percentage": saving_goal.current_amount/saving_goal.target_amount}


def get_aggregate_function_output(filtered_objects, *aggregate_function, attrb="amount") -> list:
    """
    Compute aggregate values of a field from filtered queryset using specified aggregate functions.

    Args:
    - filtered_objects (QuerySet): QuerySet containing filtered objects.
    - *aggregate_function (functions): Variable-length argument list of aggregate functions (e.g., Min, Max, Avg).

    Returns:
    - list: A list containing computed aggregate values based on the aggregate functions provided.
    """
    return [filtered_objects.aggregate(agg_value=a_fn(attrb))["agg_value"] for a_fn in aggregate_function]

def get_user_income_aggregates(user: User) -> dict: 
    """
    Retrieve minimum, maximum, and average income amounts for a given user.

    Args:
    - user (User): The user for whom income data is queried.

    Returns:
    - dict: A dictionary with keys 'min', 'max', and 'avg' representing minimum, maximum,
      and average income amounts respectively. If no income data exists for the user,
      returns {'min': 0, 'max': 0, 'avg': 0}.
    """
    aggregates = [Min, Max, Avg]
    filtered_objects = Income.objects.filter(user=user)
    today = datetime.now().strftime("%Y-%m-%d")
    if filtered_objects.exists():
        incomes_aggregates = get_aggregate_function_output(filtered_objects, *aggregates)
        dates = [Income.objects.filter(user=user, amount=amount).values("date").first() for amount in incomes_aggregates]
        dates = [date["date"].strftime("%Y-%m-%d") if date else today for date in dates]
        return {
            "min": (round(incomes_aggregates[0],3), dates[0]), 
            "max": (round(incomes_aggregates[1],3), dates[1]), 
            "avg": (round(incomes_aggregates[2],3), dates[2])
        }
    return {"min": (0, today), "max": (0, today), "avg": (0, today)}

def get_user_expense_aggregates(user: User) -> dict: 
    """
    Retrieve minimum, maximum, and average expense amounts for a given user.

    Args:
    - user (User): The user for whom expense data is queried.

    Returns:
    - dict: A dictionary with keys 'min', 'max', and 'avg' representing minimum, maximum,
      and average expense amounts respectively. If no expense data exists for the user,
      returns {'min': 0, 'max': 0, 'avg': 0}.
    """
    aggregates = [Min, Max, Avg]
    filtered_objects = Expense.objects.filter(user=user)
    today = datetime.now().strftime("%Y-%m-%d")
    if filtered_objects.exists():
        expense_aggregates = get_aggregate_function_output(filtered_objects, *aggregates)
        dates = [Expense.objects.filter(user=user, amount=amount).values("date").first() for amount in expense_aggregates]
        dates = [date["date"].strftime("%Y-%m-%d") if date else datetime.now().strftime("%Y-%m-%d") for date in dates]
        return {
            "min":(round(expense_aggregates[0],3), dates[0]), 
            "max":(round(expense_aggregates[1],3), dates[1]), 
            "avg":(round(expense_aggregates[2],3), dates[2]),
        }
    return {"min": (0, today), "max": (0, today), "avg": (0, today)}

def std(data: np.array) -> np.ndarray:
    """
    Calculate the standard deviation of a numpy array.

    Parameters:
    data (np.array): An array of numerical values.

    Returns:
    np.ndarray: The standard deviation of the input array.
    """
    return np.std(data)

def get_user_object_std(user: User, Object):
    """
    Calculate the standard deviation of the 'amount' attribute for a user's objects.

    Parameters:
    user (User): The user whose objects are being queried.
    Object: The model class of the objects being queried.

    Returns:
    float: The standard deviation of the 'amount' attribute for the user's objects.
           Returns 0 if the user has no objects.
    """
    amounts = [obj.amount for obj in Object.objects.filter(user=user)]
    if amounts: 
        return std(amounts)
    return 0

def get_user_income_std(user: User) -> float:
    """
    Calculate the standard deviation of the user's income amounts.

    Parameters:
    user (User): The user whose income is being queried.

    Returns:
    float: The standard deviation of the user's income amounts.
           Returns 0 if the user has no income records.
    """
    return get_user_object_std(user, Income)

def get_user_expense_std(user: User) -> float:
    """
    Calculate the standard deviation of the user's expense amounts.

    Parameters:
    user (User): The user whose expenses are being queried.

    Returns:
    float: The standard deviation of the user's expense amounts.
           Returns 0 if the user has no expense records.
    """
    return get_user_object_std(user, Expense)

def get_model_slope(model: LinearRegression) -> float:
    """
    Get the slope (coefficient) of a linear regression model.

    Parameters:
    model (LinearRegression): The linear regression model.

    Returns:
    float: The slope (coefficient) of the linear regression model.
           Returns 0 if the model is None.
    """
    if model: 
        return model.coef_[0]
    return 0

def get_expense_slope(user: User) -> float:
    """
    Calculate the slope of the linear regression model for the user's expenses over time.

    Parameters:
    user (User): The user whose expense data is being analyzed.

    Returns:
    float: The slope of the linear regression model for the user's expenses.
           This represents the trend of the user's expenses over time.
    """
    data = preprocess_date_data(get_user_expenses_by_date(user))
    model = train_model(data)
    return get_model_slope(model)

def get_income_slope(user: User) -> float:
    """
    Calculate the slope of the linear regression model for the user's incomes over time.

    Parameters:
    user (User): The user whose income data is being analyzed.

    Returns:
    float: The slope of the linear regression model for the user's incomes.
           This represents the trend of the user's incomes over time.
    """
    data = preprocess_date_data(get_user_incomes_by_date(user))
    model = train_model(data)
    return get_model_slope(model)


def get_expense_context(request: HttpRequest) -> dict:
    """
    Generate the context data for the expense view.

    This function aggregates user expense data, processes it for chart display,
    and prepares the context needed for rendering the expense page.

    Parameters:
    request (HttpRequest): The HTTP request object containing user information.

    Returns:
    dict: A dictionary containing the context data for the expense view.
    """
    aggregates = get_user_expense_aggregates(request.user)
    dates, amount = extrapolate_user_expenses(request.user)
    user_expenses = get_user_expenses_by_date(request.user).to_dict()
    chart_data = {"date": [date.strftime("%Y-%m-%d") for date in user_expenses["date"].values()], "amount": [float(amount) for amount in user_expenses["amount"].values()]}
    projected_chart_data = {"date": list(dates), "amount": list(amount)}
    categories = get_user_expense_categories(request.user)
    data = {
        "is_expense": True,
        "min": aggregates["min"],
        "max": aggregates["max"],
        "avg": aggregates["avg"],
        "total": calculate_total_user_expenses(request.user), 
        "std": round(get_user_expense_std(request.user),3),
        "linear_regression_slope": round(get_expense_slope(request.user),3),
        "today": datetime.now().strftime("%Y-%m-%d"),
        "chart_data": chart_data,
        "projected_chart_data": projected_chart_data, 
        "categories": categories,
        "data": [{
            "id": e.id, 
            "date": e.date.strftime("%Y-%m-%d"), 
            "amount": float(e.amount), 
            "category": e.category, 
            "description": e.description} 
            for e in Expense.objects.filter(user=request.user)
        ]
    }
    return {"datatitle": "Expense", "data": data, "active_menu": "expense"}

def get_income_context(request: HttpRequest) -> dict:
    """
    Generate the context data for the income view.

    This function aggregates user income data, processes it for chart display,
    and prepares the context needed for rendering the income page.

    Parameters:
    request (HttpRequest): The HTTP request object containing user information.

    Returns:
    dict: A dictionary containing the context data for the income view.
    """
    aggregates = get_user_income_aggregates(request.user)
    dates, amount = extrapolate_user_income(request.user)
    user_expenses = get_user_incomes_by_date(request.user).to_dict()
    chart_data = {"date": [date.strftime("%Y-%m-%d") for date in user_expenses["date"].values()], "amount": [float(amount) for amount in user_expenses["amount"].values()]}
    projected_chart_data = {"date": list(dates), "amount": list(amount)}
    categories = get_user_income_categories(request.user)
    data = {
        "is_expense": False,
        "min": aggregates["min"],
        "max": aggregates["max"],
        "avg": aggregates["avg"],
        "total": calculate_total_user_income(request.user), 
        "std": round(get_user_income_std(request.user),3),
        "linear_regression_slope": round(get_income_slope(request.user),3),
        "today": datetime.now().strftime("%Y-%m-%d"),
        "chart_data": chart_data,
        "projected_chart_data": projected_chart_data, 
        "categories": categories,
        "data": [{
            "id": i.id, 
            "date": i.date.strftime("%Y-%m-%d"), 
            "amount": float(i.amount), 
            "category": i.category, 
            "description": i.description} 
            for i in Income.objects.filter(user=request.user)
        ]
    }
    return {"datatitle": "Income", "data": data, "active_menu": "income"}

def get_saving_goal_context(request: HttpRequest) -> dict:
    """
    Generate the context data for the saving goals view.

    This function retrieves saving goals for the current user, calculates
    relevant statistics such as remaining days and percentage progress, and
    formats the data into a dictionary suitable for rendering the saving goals page.

    Parameters:
    request (HttpRequest): The HTTP request object containing user information.

    Returns:
    dict: A dictionary containing the context data for the saving goals view.
    """
    return {
    "data": [{
            "id": sg.id,  
            "name": sg.name, 
            "target_amount": float(sg.target_amount), 
            "current_amount": float(sg.current_amount), 
            "target_date": sg.target_date.strftime("%Y-%m-%d"),
            "remaining_days": sg.days_remaining,
            "percentage": round(100*float(sg.current_amount)/float(sg.target_amount),3)} 
            for sg in SavingGoal.objects.filter(user=request.user)
        ],
    "datatitle": "Saving Goals",
    "active_menu": "saving_goals"
    }
    
def calculate_average_monthly_amount(user_filtered_object):
    monthly_filtered_objects = user_filtered_object.annotate(month=TruncMonth("date")).values("month").annotate(total_income=Sum("amount")).order_by("month")
    total = sum(entry['total_income'] for entry in monthly_filtered_objects)
    number_of_months = len(monthly_filtered_objects)
    average_monthly_amount = total / number_of_months if number_of_months > 0 else 0
    return average_monthly_amount

def calculate_monthly_income(user:User):
    return calculate_average_monthly_amount(Income.objects.filter(user=user))

def calculate_monthly_expense(user:User):
    return calculate_average_monthly_amount(Expense.objects.filter(user=user))

def calculate_monthly_balance(user:User) -> float: #actually numpy.float64
    #AVG(Income - Expense) = AVG(Income) - AVG(Expense)
    monthly_income = calculate_monthly_income(user)
    monthly_expense = calculate_monthly_expense(user)
    return monthly_income - monthly_expense


def calculate_saving_goal_progress(user: User) -> float:
    saving_goals = SavingGoal.objects.filter(user=user).values("current_amount", "target_amount")
    if saving_goals.exists():
        saving_goals = pd.DataFrame(list(saving_goals), columns=("current_amount", "target_amount"))
        return round((saving_goals["current_amount"]/saving_goals["target_amount"]).mean(),2)
    return 0
    

def gather_comparison_data(user: User) -> dict:
    return {
        "total_income":calculate_total_user_income(user),
        "total_expense":calculate_total_user_expenses(user),
        "total_balance":calculate_total_user_balance(user),
        "monthly_income":calculate_monthly_income(user), 
        "monthly_expense":calculate_monthly_expense(user),
        "saving_goal_progress": calculate_saving_goal_progress(user),
        "picture_url": user.profile.profile_picture.url if user.profile.profile_picture else "/static/img/default_user.jpg"
    }

def gather_friend_data(friend: Friend) -> dict:
    friend_data = gather_comparison_data(friend.friend)
    friend_data["username"] = friend.friend.username
    friend_data["picture_url"] = friend.friend.profile.profile_picture.url if friend.friend.profile.profile_picture else "/static/img/default_user.jpg"
    return friend_data