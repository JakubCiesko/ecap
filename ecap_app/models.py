from django.contrib.auth.models import User
from django.db import models

class Product(models.Model):
    price =  models.DecimalField(max_digits=50, decimal_places=2)
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}: {self.price}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    date = models.DateField()
    amount = models.PositiveIntegerField()
    #category = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.product.name}: {self.product.price} x {self.amount}"
    
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    date = models.DateField()
    amount = models.DecimalField(max_digits=50, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return f"{self.user}: {self.category} - {self.amount} ({self.date}) (descrp: {self.description})"

class SavingGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=50, decimal_places=2)
    current_amount = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    target_date = models.DateField()
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.target_amount}"
    
class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    expenses = models.ManyToManyField(Expense, blank=True)
    incomes = models.ManyToManyField(Income, blank=True)
    total_expenses = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    total_incomes = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    total_balance = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Report for {self.user.username} from {self.start_date} to {self.end_date}"
    
    def calculate_totals(self):
        self.total_expenses = self.expenses.aggregate(total=models.Sum('amount'))['total'] or 0
        self.total_incomes = self.incomes.aggregate(total=models.Sum('amount'))['total'] or 0
        self.total_balance = self.total_incomes - self.total_expenses
        self.save()

    def populate_expenses_and_incomes(self):
        self.expenses.set(Expense.objects.filter(user=self.user, date__range=[self.start_date, self.end_date]))
        self.incomes.set(Income.objects.filter(user=self.user, date__range=[self.start_date, self.end_date]))
        self.calculate_totals()