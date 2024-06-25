from django.contrib import admin
from .models import *

admin.site.register(Expense)
admin.site.register(Product)
admin.site.register(Income)
admin.site.register(SavingGoal)
admin.site.register(Report)