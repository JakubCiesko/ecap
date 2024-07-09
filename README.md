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


![Dashboard](/screenshots/dashboard.png)
*Dashboard view in Ecap showing summary of expenses and incomes.*

