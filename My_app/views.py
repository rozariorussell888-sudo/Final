import random
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .models import PasswordResetOTP, SignupOTP, Student


def login(request):
    if request.method == "POST":
        registration_id = request.POST.get("registration_id")
        password = request.POST.get("password")

        student = Student.objects.filter(
            registration_id=registration_id, password=password
        ).first()

        if student:
            return redirect("home")
        else:
            return render(request, "Login.html", {"error": "Invalid ID or Password"})

    return render(request, "Login.html")


def signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        registration_id = request.POST.get("registration_id")
        department = request.POST.get("department")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        # Domain restriction check
        if not email.endswith("@uap-bd.edu"):
            messages.error(request, "Only UAP email allowed!")
            return redirect("signup")

        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("signup")

        if Student.objects.filter(registration_id=registration_id).exists():
            messages.error(request, "Registration ID already exists!")
            return redirect("signup")



        # Generate OTP for Signup
        otp = str(random.randint(100000, 999999))

        SignupOTP.objects.filter(email=email).delete()
        SignupOTP.objects.create(email=email, otp=otp)

        send_mail(
            "Signup Verification OTP",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
        )

        # Save signup input data in session to create user after OTP verification
        request.session["signup_data"] = request.POST.dict()

        return redirect("verify_signup_otp")

    return render(request, "Signup.html")


# ==========================================
# Signup OTP Verification View
# ==========================================
def verify_signup_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        signup_data = request.session.get("signup_data")

        if not signup_data:
            return redirect("signup")

        email = signup_data.get("email")
        otp_record = SignupOTP.objects.filter(email=email, otp=user_otp).first()

        if otp_record:
            # Create Student Account
            Student.objects.create(
                full_name=signup_data.get("full_name"),
                registration_id=signup_data.get("registration_id"),
                department=signup_data.get("department"),
                email=signup_data.get("email"),
                phone=signup_data.get("phone"),
                password=signup_data.get("password"),
            )

            # Clean up OTP and Session
            otp_record.delete()
            del request.session["signup_data"]

            messages.success(request, "Account created successfully!")
            return redirect("login")
        else:
            return render(
                request, "VerifySignupOTP.html", {"error": "Invalid or Wrong OTP"}
            )

    return render(request, "VerifySignupOTP.html")


def home(request):
    return render(request, "home.html")


# ==========================
# FORGOT PASSWORD SYSTEM
# ==========================


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        student = Student.objects.filter(email=email).first()

        if student:
            # Remove old OTP
            PasswordResetOTP.objects.filter(student=student).delete()

            # Generate new OTP
            otp = str(random.randint(100000, 999999))

            # Save OTP for this student
            PasswordResetOTP.objects.create(student=student, otp=otp)

            # Send Email
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP is {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )

            request.session["reset_email"] = email

            return redirect("verify_otp")

        else:
            return render(
                request, "ForgotPassword.html", {"error": "Email not found"}
            )

    return render(request, "ForgotPassword.html")


def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")

        email = request.session.get("reset_email")

        student = Student.objects.filter(email=email).first()

        if not student:
            return redirect("forgot_password")

        check = PasswordResetOTP.objects.filter(student=student, otp=otp).first()

        if check:
            request.session["otp_verified"] = True

            return redirect("reset_password")

        else:
            return render(request, "VerifyOTP.html", {"error": "Wrong OTP"})

    return render(request, "VerifyOTP.html")


def reset_password(request):
    if request.method == "POST":
        if not request.session.get("otp_verified"):
            return redirect("forgot_password")

        password = request.POST.get("password")

        email = request.session.get("reset_email")

        student = Student.objects.filter(email=email).first()

        if student:
            student.password = password

            student.save()

            # Delete OTP
            PasswordResetOTP.objects.filter(student=student).delete()

            # Clear session
            request.session.flush()

            messages.success(request, "Password changed successfully!")

            return redirect("login")

    return render(request, "ResetPassword.html")