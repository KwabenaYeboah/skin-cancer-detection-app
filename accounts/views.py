from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views import View
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone


from .forms import LoginForm, SignUpForm
from .models import CustomUser

class LoginView(View):
    
    def get(self, request):
        form = LoginForm()
        return render(request, "registration/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("predict")
                messages.warning(
                    request, "Account Not Activated. Check Your Email for Activation code!"
                )
                return redirect("activate")
            messages.error(request, "Wrong Email or Password!")
        return render(request, "registration/login.html", {"form": form})


class SignupView(View):
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("predict")
        form = SignUpForm()
        return render(request, "registration/signup.html", {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.verification_code = user.generate_verification_code()
            user.verification_code_expires = timezone.now() + timezone.timedelta(minutes=15)
            user.save()
            print(user)
            mail_subject = "Account Verification Code"
            message = render_to_string("registration/verification_email.html", {
                "user": user,
                "verification_code": user.verification_code,
                "expires":user.verification_code_expires,
            })
            email = EmailMessage(
                mail_subject,
                message,
                from_email="SkinCancerTeam.com",
                to=[user.email],
            )
            email.content_subtype = "html"
            email.send()

            messages.info(
                request=request,
                message="Kindly check your Email for your Account verification code!",
            )
            return redirect("activate")
        return render(request, "registration/signup.html", {"form": form})


class AccountVerificationView(View):
    def post(self, request):
        verification_code = request.POST.get("verification_code")
        try:
            user = CustomUser.objects.get(verification_code=verification_code)
            if timezone.now() > user.verification_code_expires:
                messages.error(request, "Activation code has expired. Request for a new code")
                return render(request, "registration/account_verification.html")
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None:
            user.is_active = True
            user.verification_code = None
            user.verification_code_expires = None
            user.save()
            messages.success(request, "Account successfully activated. Please Login")
            return redirect("login")
        else:
            messages.error(request, "Invalid verification code. Request for a new code")
            return render(request, "registration/account_verification.html")

    def get(self, request):
        return render(request, "registration/account_verification.html")
  
    
class ResendVerificationCodeView(View):
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_active:
                messages.info(request, "Account Already Activated. Kindly Login")
                return redirect("login")
            user.email_verification_code = user.generate_verification_code()
            user.verification_code_expires = timezone.now() + timezone.timedelta(minutes=15)
            user.save()

            # Send the activation code to the user's email
            mail_subject = "Verification Code"
            message = render_to_string("registration/verification_email.html", {
                "user": user,
                "verification_code": user.verification_code,
                "expires": user.verification_code_expires,
            })
            email = EmailMessage(
                mail_subject, message, from_email="SkinCancerTeam.com", to=[user.email]
            )
            email.content_subtype = "html"
            email.send()

            messages.success(
                request, "Activation code has been resent. Please check your email."
            )
            return redirect("activate")
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            messages.error(request, "The provided email does not exist!")
            return redirect("activate")

    def get(self, request):
        return redirect("activate")