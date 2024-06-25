from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.login_or_index, name="login_or_index"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("get_user_expenses/", views.get_user_expenses, name="get_user_expenses"),
    path("get_user_incomes/", views.get_user_incomes, name="get_user_incomes"),
    path("get_user_total_income/", views.get_user_total_income, name="get_user_total_income"),
    path("get_user_total_expense/", views.get_user_total_expense, name="get_user_total_expense"),
    path("get_user_total_balance/", views.get_user_total_balance, name="get_user_total_balance"),
    path("get_user_expected_expenses/", views.get_user_expected_expenses, name="get_user_expected_expenses"),
    path("get_user_expected_incomes/", views.get_user_expected_incomes, name="get_user_expected_incomes"),
    path("get_user_savings/", views.get_user_savings, name="get_user_savings"),
    path("get_user_report/", views.get_user_report, name="get_user_report"),
    path("create_user_report/<str:start_date>/<str:end_date>/", views.create_user_report, name="create_user_report"),
    path("print_report/<str:report_id>/", views.print_report, name="print_report"),

]