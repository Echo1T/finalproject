from django.contrib import admin
from .models import seminar, receipt, review, semPay, seminarQ
# Register your models here.
admin.site.register(seminar)
admin.site.register(receipt)
admin.site.register(review)
admin.site.register(semPay)
admin.site.register(seminarQ)