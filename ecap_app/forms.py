from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile, Expense, Income, SavingGoal

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text="Required. Enter a valid email address.")
    profile_picture = forms.ImageField(required=False)
    class Meta: 
        model = User
        fields = ("username", "email", "password1", "password2", "profile_picture")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile_picture = self.cleaned_data.get("profile_picture")
            if profile_picture:
                Profile.objects.create(user=user, profile_picture=profile_picture)
            else:
                Profile.objects.create(user=user)
        return user
    

class ExpenseForm(forms.ModelForm):
    class Meta: 
        model = Expense
        fields = ["date", "amount", "category", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
        }
    

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ["date", "amount", "category", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
        }


class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ["name", "target_amount", "current_amount", "target_date"]
        widgets = {
            "target_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "target_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "current_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserUpdateForm(UserChangeForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank if you do not wish to change the password.")
    class Meta:
        model = User
        fields = ["username", "email", "password"]
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_picture", "bio"]