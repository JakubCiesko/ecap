# Ecap - Personal Budget Tracker

Ecap is a web application built using Django that serves as a personal budget tracker. It allows users to manage their incomes, expenses, savings goals, and generate financial reports.

## Features

- **User Authentication**: Secure user registration and login system using Django's built-in authentication system.
- **Expense Management**: Track and manage expenses with the ability to add, delete, and view detailed expense entries.
- **Income Management**: Track and manage incomes with similar functionalities as expenses.
- **Saving Goals**: Set and track saving goals, monitor progress towards targets.
- **Financial Reports**: Generate detailed financial reports based on user-defined periods.
- **Messaging**: Basic messaging feature to communicate within the application.
- **Responsive Design**: Built with responsive design principles to ensure usability across devices.

## Installation

To run Ecap locally or on your server, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/JakubCiesko/ecap.git
   cd Ecap

2. **Set up a virtual environment:**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt

4. **Set up the database:**

   ```bash
   python manage.py migrate
   
6. **Create a superuser (admin):**

    ```bash
   python manage.py createsuperuser
7. **Run the development server:**

   ```bash
   python manage.py runserver

## Screenshots of the app
<p align="center">
  <img src="https://raw.githubusercontent.com/JakubCiesko/ecap/docs-assets/screenshots/sign_in_index.gif" alt="SignInDashboard" width="600"/>
  <br>
  <em>Sign In and Dashboard view showing summary of expenses and incomes, and all the related statistics.</em>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/JakubCiesko/ecap/docs-assets/screenshots/income_expense.gif" alt="IncomeExpenseView" width="600"/>
  <br>
  <em>Income and Expense views showing summary of expenses and incomes.</em>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/JakubCiesko/ecap/docs-assets/screenshots/saving_goal_view.gif" alt="SavingGoalView" width="600"/>
  <br>
  <em>Saving Goal View showing summary of Saving Goals. Saving Goals can be set and deleted by the user. Their progress is displayed using doughnut charts.</em>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/JakubCiesko/ecap/docs-assets/screenshots/chat.png" alt="ChatView" width="600"/>
  <br>
  <em>You can also connect with others via chat.</em>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/JakubCiesko/ecap/docs-assets/screenshots/compare_view.gif" alt="CompareView" width="600"/>
  <br>
  <em>Comparison with your friends.</em>
</p>

