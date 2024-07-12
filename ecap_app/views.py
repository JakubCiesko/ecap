import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.templatetags.static import static
from datetime import datetime
from .models import *
from .utils import *
from .forms import SignUpForm, ExpenseForm, IncomeForm, SavingGoalForm
from transformers import pipeline


print("Loading model")
checkpoint = "MBZUAI/LaMini-Flan-T5-248M"
model = pipeline("text2text-generation", model=checkpoint)
print("Everything loaded, ask away!")

def generate_response(prompt: str) -> str:
    """
    Generate a response based on the given prompt using a pre-trained text generation model.

    Parameters:
    prompt (str): The prompt or input text for generating the response.

    Returns:
    str: The generated response text based on the input prompt.
    """
    return model(
        prompt,
        max_new_tokens=500,  
        num_return_sequences=1,  
        temperature=0.7,  
        top_k=50,  
        top_p=0.95,
    )

def login_or_index(request):
    """
    View function for handling user login or rendering login form.

    If the user is already authenticated, it renders the 'index.html' template with the
    active menu set to 'login_or_index'. If the request method is POST, it attempts to
    authenticate the user using the provided form data. Upon successful authentication,
    the user is logged in and redirected to the 'login_or_index' view. If the request
    method is GET, it renders the 'login.html' template with an AuthenticationForm.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    HttpResponse: Rendered HTML response based on user authentication status and form validation.
    """
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
    """
    View function for rendering the dashboard (index) page.

    Renders the 'index.html' template with the active menu set to 'dashboard'.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    HttpResponse: Rendered HTML response for the dashboard page.
    """
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
    """
    View function for handling user registration and rendering signup form.

    If the request method is POST, it attempts to validate and save user registration
    form data. Upon successful registration, the user is logged in and redirected to
    the 'login_or_index' view. If the request method is GET, it renders the 'signup.html'
    template with an empty SignUpForm.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    HttpResponse: Rendered HTML response based on user registration status and form validation.
    """
    user = request.user
    try:
        user_expenses = get_user_expenses_by_date(user).to_dict()
        return JsonResponse({"date": user_expenses["date"], "amount": user_expenses["amount"]})
    except KeyError:
        return JsonResponse({"error": "No expenses data found for the user."}, status=200)

@login_required
def get_user_incomes(request):
    """
    Retrieves and returns the user's income data as JSON response.

    Fetches income data for the authenticated user using `get_user_incomes_by_date`
    function and converts it to a dictionary. If successful, returns a JsonResponse
    containing dates and corresponding amounts. If no data is found, returns a JsonResponse
    with an error message and status code 200.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    JsonResponse: JSON response containing user's income data or an error message.
    """
    user = request.user
    try:
        user_incomes = get_user_incomes_by_date(user).to_dict()
        return JsonResponse({"date": user_incomes["date"], "amount": user_incomes["amount"]})
    except KeyError:
        return JsonResponse({"error": "No incomes data found for the user."}, status=200)

@login_required
def get_user_total_income(request):
    """
    Retrieves and returns the total income of the authenticated user as JSON response.

    Calculates the total income using `calculate_total_user_income` function and returns
    it as a JsonResponse.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    JsonResponse: JSON response containing total income of the user.
    """
    user = request.user
    return JsonResponse({"user_income": calculate_total_user_income(user)})

@login_required
def get_user_total_expense(request):
    """
    Retrieves and returns the total expenses of the authenticated user as JSON response.

    Calculates the total expenses using `calculate_total_user_expenses` function and returns
    it as a JsonResponse.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    JsonResponse: JSON response containing total expenses of the user.
    """
    user = request.user
    return JsonResponse({"user_expense": calculate_total_user_expenses(user)})

@login_required
def get_user_total_balance(request):
    """
    Retrieves and returns the total balance of the authenticated user as JSON response.

    Calculates the total balance using `calculate_total_user_balance` function and returns
    it as a JsonResponse.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    JsonResponse: JSON response containing total balance of the user.
    """
    user = request.user
    return JsonResponse({"user_balance": calculate_total_user_balance(user)})

@login_required
def get_user_expected_expenses(request):
    """
    Retrieves and returns the expected expenses of the authenticated user for the next 10 days as JSON response.

    Extrapolates expected expenses using `extrapolate_user_expenses` function for the next 10 days
    and returns dates and corresponding amounts as a JsonResponse. If no expenses are found, returns
    a JsonResponse with an error message and status code 200.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    JsonResponse: JSON response containing expected expenses of the user for the next 10 days or an error message.
    """
    user = request.user
    try:
        dates, amount = extrapolate_user_expenses(user, 10)
        return JsonResponse({"date": list(dates), "amount": list(amount)})
    except KeyError:
        return JsonResponse({"error": "No user expenses"}, status=200)

@login_required
def get_user_expected_incomes(request):
    """
    Retrieves and returns the expected incomes of the authenticated user for the next 10 days as JSON response.

    Extrapolates expected incomes using `extrapolate_user_income` function for the next 10 days
    and returns dates and corresponding amounts as a JsonResponse. If no incomes are found, returns
    a JsonResponse with an error message and status code 200.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    JsonResponse: JSON response containing expected incomes of the user for the next 10 days or an error message.
    """
    user = request.user
    try:
        dates, amount = extrapolate_user_income(user, 10)
        return JsonResponse({"date": list(dates), "amount": list(amount)})
    except KeyError:
        return JsonResponse({"error": "No user incomes"}, status=200)

@login_required
def get_user_savings(request):
    """
    Retrieves and returns the saving goals of the authenticated user as JSON response.

    Fetches saving goals from `SavingGoal` model filtered by the authenticated user and returns
    current and target amounts for each saving goal as a JsonResponse.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    JsonResponse: JSON response containing saving goals of the user with current and target amounts.
    """
    user = request.user
    saving_goals = SavingGoal.objects.filter(user=user)
    return JsonResponse({"saving_goals":[{"current": saving_goal.current_amount, "target": saving_goal.target_amount} for saving_goal in saving_goals]})

@login_required
def get_user_report(request):
    """
    Retrieves and returns the reports of the authenticated user as JSON response.

    Fetches reports from `Report` model filtered by the authenticated user and constructs
    a list of report data containing username, report ID, start and end dates, total expenses,
    total incomes, and lists of expenses and incomes as JSON response. Reports are sorted by ID.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
    JsonResponse: JSON response containing reports of the user with detailed report data.
    """
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
    """
    Creates and returns a new report for the authenticated user for the specified date range as JSON response.

    Creates a new report using `create_report_for_user` function for the authenticated user with the provided
    start and end dates. Constructs report data containing username, report ID, start and end dates, total expenses,
    total incomes, and lists of expenses and incomes. Returns the newly created report data as a JsonResponse with status 200.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.
    start_date (str): Start date of the report in "YYYY-MM-DD" format.
    end_date (str): End date of the report in "YYYY-MM-DD" format.

    Returns:
    JsonResponse: JSON response containing newly created report data.
    """
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
    """
    Renders and returns the report template for the authenticated user as HTTP response.

    Fetches the report with the specified report_id from `Report` model. If the authenticated user is
    the owner of the report, renders the report template with the report context and returns it as
    an HTTP response. Otherwise, returns HTTP 403 Forbidden status.

    Parameters:
    request (HttpRequest): The HTTP request object containing metadata about the request.
    report_id (int): ID of the report to be rendered.

    Returns:
    HttpResponse: Rendered report template as HTTP response or HTTP 403 Forbidden if user is not authorized.
    """
    user = request.user
    report = get_object_or_404(Report, pk=report_id)
    if report.user.id == user.id:
        context = {
        "report": report,   #add charts?
        }
        return render(request, "report_template.html", context=context)
    return HttpResponse(status=403)

@login_required
def process_message(request):
    """
    Handles incoming POST requests containing a JSON payload with a 'message' key.
    Uses the message to generate a response and returns it as a JSON response.

    Args:
        request (HttpRequest): The HTTP request object containing the POST data.

    Returns:
        JsonResponse: A JSON response containing the generated chatbot response.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        chat_input = generate_response(user_message)
        response = chat_input[0]["generated_text"]
        return JsonResponse({"success": True, "response": response})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@login_required
def chat_list(request):
    """
    Retrieves the list of chats associated with the current authenticated user.
    Constructs a JSON response containing chat details including usernames and profile picture URLs.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of chats with their details.
    """
    user = request.user
    chats = Chat.objects.filter(user1 = user.id) | Chat.objects.filter(user2 = user.id)
    user_id = user.id
    default_profile_picture_url = static("img/default_user.jpg")
    pick_different_user = lambda chat: chat.user1.id == user_id  
    get_profilepic_url = lambda user: user.profile.profile_picture.url if hasattr(user, "profile") and user.profile.profile_picture and user.profile.profile_picture.name  else default_profile_picture_url
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
    """
    Retrieves the percentage distribution of expense categories for the current authenticated user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the percentage distribution of expense categories.
    """
    return JsonResponse({"data": get_user_expense_categories(request.user)})

@login_required
def income_category_percentage(request):
    """
    Retrieves the percentage distribution of income categories for the current authenticated user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the percentage distribution of income categories.
    """
    return JsonResponse({"data": get_user_income_categories(request.user)})

@login_required
def saving_goal(request):
    """
    Retrieves the saving goal details for the current authenticated user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the saving goal details.
    """
    try: 
        return JsonResponse(get_saving_goal(request.user))
    except AttributeError:
        return JsonResponse({"error": "No saving goal found"}, status=200)

@login_required
def messages(request, conversation_id):
    """
    Retrieves messages for a specific conversation and renders them in the 'messages.html' template.

    Args:
        request (HttpRequest): The HTTP request object.
        conversation_id (int): The ID of the conversation for which messages are to be retrieved.

    Returns:
        HttpResponse: A rendered HTTP response displaying messages for the conversation.
    """
    user = request.user
    messages, other_chats = [], []
    other_user = None
    chats = Chat.objects.filter((Q(user1=user) | Q(user2=user)))
    if chats:
        chat = chats.filter(Q(id=conversation_id)).first()
        other_chats = chats.exclude(id=conversation_id)
        messages = chat.messages.order_by("timestamp")
        other_user = chat.user1 if chat.user1 != user else chat.user2
    return render(request, "messages.html", context={
        "chat": chat, 
        "messages":messages, 
        "other_user":other_user,
        "other_chats":other_chats,
        "active_menu": "general_messages"
    })

@login_required
def general_messages(request):
    """
    Retrieves the general messages for the authenticated user's first chat and renders them in the 'messages.html' template.

    If the user has chats, retrieves the first chat and its messages, along with other chats and the username of the other user in the chat.
    Renders these details along with the 'messages.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A rendered HTTP response displaying messages for the user's first chat.
    """
    user = request.user
    messages, other_chats = [], []
    other_user = None
    chat = None
    chats = Chat.objects.filter((Q(user1=user) | Q(user2=user)))
    users = User.objects.exclude(id=user.id)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        other_user = User.objects.get(id=user_id)
        chat = Chat.objects.filter(user1=user, user2=other_user).first() or \
               Chat.objects.filter(user1=other_user, user2=user).first()
        if not chat:
            chat = Chat.objects.create(user1=user, user2=other_user)

    if chats.exists(): #added .exists()
        chat = chats.first()
        other_chats = chats.exclude(id=chat.id)
        messages = chat.messages.order_by("timestamp")
        other_user = chat.user1 if chat.user1 != user else chat.user2
    return render(request, "messages.html", context={
        "chat": chat, 
        "messages": messages, 
        "other_user": other_user,
        "other_chats": other_chats,
        "users": users,
        "active_menu": "general_messages"
    })

@login_required
def send_message(request):
    """
    Handles sending messages to a specific chat identified by the chat_id parameter via a POST request.

    Retrieves the chat using the chat_id, checks if the authenticated user is a participant in the chat.
    Creates a new message object and saves it to the database.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the sender username, message content, and timestamp of the sent message.
    """
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
    """
    Handles the income data input form submission via POST or renders the form for GET requests.

    If the request method is POST, validates the IncomeForm data and saves the income entry for the authenticated user.
    If the form is valid, redirects to the 'income' page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'data_input_form.html' template with the income data input form.
    """
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
    """
    Handles the expense data input form submission via POST or renders the form for GET requests.

    If the request method is POST, validates the ExpenseForm data and saves the expense entry for the authenticated user.
    If the form is valid, redirects to the 'expense' page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'data_input_form.html' template with the expense data input form.
    """
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
    """
    Deletes selected expense items based on POST request data.

    Retrieves selected expense item IDs from POST data and deletes corresponding Expense objects.
    Redirects to the 'expense' page after deletion.

    Args:
        request (HttpRequest): The HTTP request object containing selected expense item IDs.

    Returns:
        HttpResponseRedirect: Redirects to the 'expense' page.

    """
    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")
        selected_items = [item for item in selected_items if item]
        if selected_items:
            Expense.objects.filter(id__in=selected_items).delete()
    return redirect("expense")

@login_required
def delete_selected_incomes(request):
    """
    Deletes selected income items based on POST request data.

    Retrieves selected income item IDs from POST data and deletes corresponding Income objects.
    Redirects to the 'income' page after deletion.

    Args:
        request (HttpRequest): The HTTP request object containing selected income item IDs.

    Returns:
        HttpResponseRedirect: Redirects to the 'income' page.

    """
    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")
        selected_items = [item for item in selected_items if item]
        if selected_items:
            Income.objects.filter(id__in=selected_items).delete()
    return redirect("income")


@login_required
def delete_selected_reports(request):
    """
    Deletes selected report items based on POST request data.

    Retrieves selected report item IDs from POST data and deletes corresponding Report objects.
    Returns a JSON response indicating success or failure of the deletion operation.

    Args:
        request (HttpRequest): The HTTP request object containing selected report item IDs in JSON format.

    Returns:
        JsonResponse: A JSON response indicating the status of the deletion operation.

    """
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
    """
    Renders the saving goal creation form or handles its submission via POST request.

    If the request method is POST, validates the SavingGoalForm data and saves the saving goal entry for the authenticated user.
    If the form is valid, redirects to the 'saving_goal_view' page.
    Renders the 'saving_goal.html' template with the SavingGoalForm.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'saving_goal.html' template with the saving goal creation form.

    """
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
    """
    Deletes selected saving goal items based on POST request data.

    Retrieves selected saving goal item IDs from POST data and deletes corresponding SavingGoal objects.
    Redirects to the 'saving_goal_view' page after deletion.

    Args:
        request (HttpRequest): The HTTP request object containing selected saving goal item IDs.

    Returns:
        HttpResponseRedirect: Redirects to the 'saving_goal_view' page.

    """
    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")
        selected_items = [item for item in selected_items if item]
        if selected_items:
            SavingGoal.objects.filter(id__in=selected_items).delete()
    return redirect("saving_goal_view")

@login_required
def user_list(request):
    """
    View that returns a JSON response containing a list of all users except the current user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of users with their IDs and usernames, excluding the current user.
    """
    users = User.objects.exclude(id=request.user.id)
    return JsonResponse([{"id": u.id, "username": u.username} for u in users], safe=False)

@login_required
def start_chat(request, user_id):
    """
    View that starts a chat with another user or redirects to an existing chat if one already exists.

    Args:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the other user to start a chat with.

    Returns:
        HttpResponseRedirect: A redirect to the messages view with the conversation ID of the existing or new chat.
    """
    other_user = User.objects.filter(id=user_id)
    existing_chat = Chat.objects.filter(user1 = request.user, user2=other_user).first() | Chat.objects.filter(user2 = request.user, user1=other_user).first()
    if existing_chat:
        return redirect("messages", conversation_id=existing_chat.id)
    new_chat = Chat.objects.create(user1=request.user, user2=other_user)
    return redirect("messages", conversation_id=new_chat.id)

@login_required
def compare(request):
    """
    View that compares the current user with their friends and renders the comparison page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered comparison page with the user and friends' data.
    """
    user = request.user 
    user_data = gather_comparison_data(user)
    friend_relations = Friend.objects.filter((Q(user=user) | Q(friend=user)), status="accepted")#user.friends.all()
    friends = [
        friend_relation.friend if friend_relation.user == user else friend_relation.user
        for friend_relation in friend_relations
    ]
    friends_data = [gather_friend_data(friend) for friend in friends]
    other_users = User.objects.exclude(id=request.user.id)
    friend_requests = Friend.objects.filter(friend=request.user, status="pending")
    context = {
        "user_data": user_data, 
        "friends": friends_data, 
        "friend_requests": friend_requests,
        "other_users": other_users,
        "active_menu": "comparison"
    }
    return render(request, "compare.html", context=context)

@login_required
def send_friend_request(request):
    """
    View to handle sending a friend request.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered comparison page with the user and friends' data.
    """
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        Friend.objects.get_or_create(user=request.user, friend=user, status='pending')
        #created? if not... already exists
    return redirect("comparison") 

@login_required
def accept_friend_request(request, friend_request_id):
    """
    View to handle accepting a friend request.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered comparison page with the user and friends' data.
    """
    friend_request = get_object_or_404(Friend, id=friend_request_id, friend=request.user)
    friend_request.status = "accepted"
    friend_request.save()
    return redirect("comparison")

@login_required
def reject_friend_request(request, friend_request_id):
    """
    View to handle rejecting a friend request.
    
    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered comparison page with the user and friends' data.
    """
    friend_request = get_object_or_404(Friend, id=friend_request_id, friend=request.user)
    friend_request.status = "rejected"
    friend_request.save()
    return redirect("comparison")
