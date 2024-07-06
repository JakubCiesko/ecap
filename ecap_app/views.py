import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.templatetags.static import static
#from django.template.loader import render_to_string
from datetime import datetime
from .models import *
from .utils import *
from .forms import SignUpForm, ExpenseForm, IncomeForm, SavingGoalForm
from transformers import pipeline


print("Loading model")
checkpoint = "MBZUAI/LaMini-Flan-T5-248M"
model = lambda x: x#pipeline("text2text-generation", model=checkpoint)
print("Everything loaded, ask away!")

def generate_response(prompt):
    return model(
        prompt,
        max_new_tokens=500,  # Adjust this value based on your needs
        num_return_sequences=1,  # Number of responses to generate
        temperature=0.7,  # Control randomness in the response
        top_k=50,  # Consider top_k tokens with highest probability
        top_p=0.95,  # Consider tokens with cumulative probability above this threshold ADD do_sample=True
    )


def login_or_index(request):
    if request.user.is_authenticated:
        return render(request, "index.html", context={"active_menu": "login_or_index"})
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
    return render(request, "index.html", context={"active_menu": "dashboard"})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
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
    try:
        user_expenses = get_user_expenses_by_date(user).to_dict()
        return JsonResponse({"date": user_expenses["date"], "amount": user_expenses["amount"]})
    except KeyError:
        return JsonResponse({"error": "No expenses data found for the user."}, status=200)

@login_required
def get_user_incomes(request):
    user = request.user
    try:
        user_incomes = get_user_incomes_by_date(user).to_dict()
        return JsonResponse({"date": user_incomes["date"], "amount": user_incomes["amount"]})
    except KeyError:
        return JsonResponse({"error": "No incomes data found for the user."}, status=200)

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
    try:
        dates, amount = extrapolate_user_expenses(user, 10)
        return JsonResponse({"date": list(dates), "amount": list(amount)})
    except KeyError:
        return JsonResponse({"error": "No user expenses"}, status=200)

@login_required
def get_user_expected_incomes(request):
    user = request.user
    try:
        dates, amount = extrapolate_user_income(user, 10)
        return JsonResponse({"date": list(dates), "amount": list(amount)})
    except KeyError:
        return JsonResponse({"error": "No user incomes"}, status=200)

@login_required
def get_user_savings(request):
    user = request.user
    saving_goals = SavingGoal.objects.filter(user=user)
    return JsonResponse({"saving_goals":[{"current": saving_goal.current_amount, "target": saving_goal.target_amount} for saving_goal in saving_goals]})

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
    return JsonResponse(sorted(report_data, key=lambda x: x["id"]), safe=False)

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
        return render(request, "report_template.html", context=context)
    return HttpResponse(status=403)

@login_required
def process_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        chat_input = generate_response(user_message)
        response = chat_input[0]["generated_text"]
        return JsonResponse({"success": True, "response": response})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@login_required
def chat_list(request):
    user = request.user
    chats = Chat.objects.filter(user1 = user.id) | Chat.objects.filter(user2 = user.id)
    user_id = user.id
    default_profile_picture_url = static("img/default_user.jpg")
    pick_different_user = lambda chat: chat.user1.id == user_id  
    get_profilepic_url = lambda user: user.profile.profile_picture.url if hasattr(user, "profile") else default_profile_picture_url
    chats = [{
        "chat_id": chat.id, 
        "user1": chat.user1.username, 
        "user2": chat.user2.username, 
        "different_user": [chat.user1.username, chat.user2.username][pick_different_user(chat)],
        "different_user_profilepic_url": get_profilepic_url([chat.user1, chat.user2][pick_different_user(chat)])} 
        for chat in chats],

    return JsonResponse({"chats": chats})


@login_required
def expense_category_percentage(request):
    return JsonResponse({"data": get_user_expense_categories(request.user)})

@login_required
def income_category_percentage(request):
    return JsonResponse({"data": get_user_income_categories(request.user)})

@login_required
def saving_goal(request):
    try: 
        return JsonResponse(get_saving_goal(request.user))
    except AttributeError:
        return JsonResponse({"error": "No saving goal found"}, status=200)

@login_required
def messages(request, conversation_id):
    user = request.user
    messages, other_chats = [], []
    other_user_username = ""
    chats = Chat.objects.filter((Q(user1=user) | Q(user2=user)))
    if chats:
        chat = chats.filter(Q(id=conversation_id)).first()
        other_chats = chats.exclude(id=conversation_id)
        messages = chat.messages.order_by("timestamp")
        other_user_username = chat.user1.username if chat.user1 != user else chat.user2.username
    return render(request, "messages.html", context={
        "chat": chat, 
        "messages":messages, 
        "other_user":other_user_username,
        "other_chats":other_chats,
        "active_menu": "general_messages"
    })

@login_required
def general_messages(request):
    user = request.user
    messages, other_chats = [], []
    other_user_username = ""
    chat = None
    chats = Chat.objects.filter((Q(user1=user) | Q(user2=user)))
    if chats:
        chat = chats.first()
        other_chats = chats.exclude(id=chat.id)
        messages = chat.messages.order_by("timestamp")
        other_user_username = chat.user1.username if chat.user1 != user else chat.user2.username
    return render(request, "messages.html", context={
        "chat": chat, 
        "messages":messages, 
        "other_user": other_user_username,
        "other_chats":other_chats,
        "active_menu": "general_messages"
    })

@login_required
def send_message(request):
    if request.method == "POST":
        chat_id = request.POST.get("chat_id")
        content = request.POST.get("content")
        chat = get_object_or_404(Chat, id=chat_id)
        if request.user not in [chat.user1, chat.user2]:
            return JsonResponse({"error": "You are not part of this chat."}, status=403)
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=content
        )
        return JsonResponse({
            "sender": message.sender.username,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def income(request):
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user 
            income.save()
            return redirect("income")
    else: 
        form = IncomeForm()
    context = get_income_context(request)
    context["form"] = form 
    return render(request, "data_input_form.html", context=context)

@login_required
def expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user 
            expense.save()
            return redirect("expense")
    else: 
        form = ExpenseForm()
    context = get_expense_context(request)
    context["form"] = form
    return render(request, "data_input_form.html", context=context)


@login_required
def delete_selected_expenses(request):
    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")
        selected_items = [item for item in selected_items if item]
        if selected_items:
            Expense.objects.filter(id__in=selected_items).delete()
    return redirect("expense")

@login_required
def delete_selected_incomes(request):
    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")
        selected_items = [item for item in selected_items if item]
        if selected_items:
            Income.objects.filter(id__in=selected_items).delete()
    return redirect("income")


@login_required
def delete_selected_reports(request):
    if request.method == "POST":
        data = json.loads(request.body)
        selected_items = data.get("selected_items", [])
        if selected_items:
            Report.objects.filter(id__in=selected_items).delete()
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({"status": "no items selected"}, status=400)
    return JsonResponse({"status": "invalid request"}, status=400)


@login_required
def saving_goal_view(request):
    if request.method == "POST":
        form = SavingGoalForm(request.POST)
        if form.is_valid():
            saving_goal = form.save(commit=False)
            saving_goal.user = request.user 
            saving_goal.save()
            return redirect("saving_goal_view")
    else: 
        form = SavingGoalForm()
    context = get_saving_goal_context(request)
    context["form"] = form
    return render(request, "saving_goal.html", context=context)

@login_required
def delete_selected_saving_goals(request):
    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")
        selected_items = [item for item in selected_items if item]
        if selected_items:
            SavingGoal.objects.filter(id__in=selected_items).delete()
    return redirect("saving_goal_view")