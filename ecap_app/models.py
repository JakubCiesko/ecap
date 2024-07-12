import uuid
import os
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.templatetags.static import static


class Product(models.Model):
    price =  models.DecimalField(max_digits=50, decimal_places=2)
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}: {self.price}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    #product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    date = models.DateField()
    amount = models.DecimalField(max_digits=50, decimal_places=2) #amount = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.user}: {self.amount}"
    
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

    @property
    def days_remaining(self):
        if self.target_date > timezone.now().date():
            return (self.target_date - timezone.now().date()).days
        else:
            return 0

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
        self.total_expenses = self.expenses.annotate(total_cost=models.F("amount")).aggregate(total=models.Sum("total_cost"))["total"] or 0
        self.total_incomes = self.incomes.aggregate(total=models.Sum("amount"))["total"] or 0
        self.total_balance = self.total_incomes - self.total_expenses
        
    def populate_expenses_and_incomes(self):
        self.expenses.set(Expense.objects.filter(user=self.user, date__range=[self.start_date, self.end_date]))
        self.incomes.set(Income.objects.filter(user=self.user, date__range=[self.start_date, self.end_date]))
        self.calculate_totals()

    
class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name="conversations_started", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="conversations_joined", on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_chat",
                condition=models.Q(user1__lt=models.F("user2"))
            ),
        ]
    
    def save(self, *args, **kwargs):
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1
        super(Chat, self).save(*args, **kwargs)

    def __str__(self):
        return f"Conversation between {self.user1.username} and {self.user2.username}"
    
class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender} in chat {self.chat.id} at {self.timestamp}"

def get_profile_picture_filepath(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("profile_pictures/", filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to=get_profile_picture_filepath, 
        blank=False, 
        null=False,
        default="profile_pictures/default_user.jpg"
    )
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
class Friend(models.Model):
    user = models.ForeignKey(User, related_name="friends", on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name="user_friends", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")], default="pending")

    def __str__(self):
        return f"{self.user} - {self.friend} ({self.status})"
    
    class Meta:
        unique_together = ("user", "friend")

