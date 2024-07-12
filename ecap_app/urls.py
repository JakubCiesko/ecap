from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "404.html", status=404)

handler404 = custom_404

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
    path("report/<str:report_id>/", views.print_report, name="print_report"),
    path("process_message/", views.process_message, name="process_message"),
    path("chat_list/", views.chat_list, name="chat_list"),
    path("expense_category/", views.expense_category_percentage, name="expense_category_percentage"),
    path("income_category/", views.income_category_percentage, name="income_category_percentage"),
    path("saving_goal/", views.saving_goal, name="saving_goal"),
    path("messages/<str:conversation_id>/", views.messages, name="messages"),
    path("messages/", views.general_messages, name="general_messages"),
    path("send_message/", views.send_message, name="send_message"),
    path("income/", views.income, name="income"),
    path("expense/", views.expense, name="expense"),
    path("comparison/", views.compare, name="comparison"),
    path("saving_goals/", views.saving_goal_view, name="saving_goal_view"),
    path("delete_selected_expenses/", views.delete_selected_expenses, name="delete_selected_expenses"),
    path("delete_selected_incomes/", views.delete_selected_incomes, name="delete_selected_incomes"),
    path("delete_selected_reports/", views.delete_selected_reports, name="delete_selected_reports"),
    path("delete_selected_saving_goals/", views.delete_selected_saving_goals, name="delete_selected_saving_goals"),
    path("start_chat/<str:user_id>/", views.start_chat, name="start_chat"),
    path("user_list/", views.user_list, name="user_list"),
    path("send_friend_request/", views.send_friend_request, name="send_friend_request"),
    path("accept_friend_request/<str:friend_request_id>", views.accept_friend_request, name="accept_friend_request"),
    path("reject_friend_request/<str:friend_request_id>", views.reject_friend_request, name="reject_friend_request"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)