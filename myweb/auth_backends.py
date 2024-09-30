from django.contrib.auth.backends import BaseBackend
from .models import Student
from django.contrib.auth.hashers import check_password

class StudentBackend(BaseBackend):
    def authenticate(self, request, reg_no=None, password=None):
        try:
            student = Student.objects.get(reg_no=reg_no)
            if student and check_password(password, student.password):
                return student
        except Student.DoesNotExist:
            return None

    def get_user(self, student_id):
        try:
            return Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return None
