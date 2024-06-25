from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, FileResponse
from django.template.loader import render_to_string
from datetime import datetime
from .models import *
from .utils import *
from .forms import SignUpForm


def expense_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    date_str = request.GET.get("date", "2024-01-01")  
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_date = datetime.now().date()
    days_to_predict = 30  # Predict for the next 30 days
    future_dates, predicted_expenses = extrapolate_user_expenses(user, start_date, days_to_predict)
    predictions = zip(future_dates, predicted_expenses)
    user = get_object_or_404(User, id=user_id)
    balance_data = calculate_user_balance_over_time(user)
    return render(request, "expense_list.html", {"balance_data": balance_data.to_dict("records")})

def login_or_index(request):
    if request.user.is_authenticated:
        return render(request, "index.html")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("login_or_index")
    else: 
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

@login_required
def index(request):
    return render(request, "index.html")

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.email = form.cleaned_data.get("email")
            user.save()
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect("login_or_index")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

@login_required
def get_user_expenses(request):
    user = request.user
    user_expenses = get_user_expenses_by_date(user).to_dict()
    return JsonResponse({"user_expenses": user_expenses})

@login_required
def get_user_incomes(request):
    user = request.user
    user_incomes = get_user_incomes_by_date(user).to_dict()
    return JsonResponse({"user_incomes": user_incomes})

@login_required
def get_user_total_income(request):
    user = request.user
    return JsonResponse({"user_income": calculate_total_user_income(user)})

@login_required
def get_user_total_expense(request):
    user = request.user
    return JsonResponse({"user_expense": calculate_total_user_expenses(user)})

@login_required
def get_user_total_balance(request):
    user = request.user
    return JsonResponse({"user_balance": calculate_total_user_balance(user)})

@login_required
def get_user_expected_expenses(request):
    user = request.user
    dates, amount = extrapolate_user_expenses(user, 10)
    return JsonResponse({"user_expected_expenses": {"dates": list(dates), "amount": list(amount)}})

@login_required
def get_user_expected_incomes(request):
    user = request.user
    dates, amount = extrapolate_user_income(user, 10)
    return JsonResponse({"user_expected_expenses": {"dates": list(dates), "amount": list(amount)}})

@login_required
def get_user_savings(request):
    user = request.user
    saving_goals = SavingGoal.objects.filter(user=user)
    current_amounts = [saving_goal.current_amount for saving_goal in saving_goals]
    target_amounts = [saving_goal.target_amount for saving_goal in saving_goals]
    return JsonResponse({"user_savings": {"current": current_amounts, "goal": target_amounts}})

@login_required
def get_user_report(request):
    user = request.user
    reports = Report.objects.filter(user=user)
    report_data = [{
        "user": report.user.username,
        "id": report.id,
        "start_date": report.start_date,
        "end_date": report.end_date,
        "total_expenses": report.total_expenses,
        "total_incomes": report.total_incomes,
        "expenses": list(report.expenses.values("date", "amount")),
        "incomes": list(report.incomes.values("date", "amount")),
    } for report in reports] 
    return JsonResponse(report_data, safe=False)

@login_required
def create_user_report(request, start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    report = create_report_for_user(request.user, start_date, end_date)
    
    report_data = {
        "user": report.user.username,
        "id": report.id,
        "start_date": report.start_date,
        "end_date": report.end_date,
        "total_expenses": report.total_expenses,
        "total_incomes": report.total_incomes,
        "expenses": list(report.expenses.values("date", "amount")),
        "incomes": list(report.incomes.values("date", "amount")),
    }
    return JsonResponse({"report": report_data}, status=200)
    
@login_required
def print_report(request, report_id):
    user = request.user
    report = get_object_or_404(Report, pk=report_id)
    if report.user.id == user.id:
        context = {
        "report": report,
        }
        pdf_file = pdfkit.from_string("<p>helloworld</p>")
        return FileResponse(pdf_file)
    return HttpResponse(status=403)