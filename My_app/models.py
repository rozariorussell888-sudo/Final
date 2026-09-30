from django.db import models
from django.utils import timezone



class Student(models.Model):

    full_name = models.CharField(max_length=100)

    registration_id = models.CharField(
        max_length=50,
        unique=True
    )

    department = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15
    )

    password = models.CharField(
        max_length=128
    )


    def __str__(self):
        return self.registration_id




class PasswordResetOTP(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    otp = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )


    def __str__(self):
        return self.student.email



class SignupOTP(models.Model):

    email = models.EmailField()

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.email