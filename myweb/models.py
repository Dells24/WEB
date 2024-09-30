# models.py
from django.db import models
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)

        if extra_fields.get('is_superuser') is True:
            raise ValueError('Superuser cannot have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Student(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    reg_no = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    graduation_year = models.CharField(max_length=4, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'reg_no']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='student_set',  # Unique related_name for groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='student_permissions_set',  # Unique related_name for user_permissions
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.reg_no}"

    def save(self, *args, **kwargs):
        if not self.password:
            plain_password = get_random_string(length=6)
            self.password = make_password(plain_password)
            self.send_password_email(plain_password)
        super(Student, self).save(*args, **kwargs)

    def send_password_email(self, plain_password):
        subject = "Your Voting Account Details"
        message = f"""
        Dear {self.name},

        Your voting account has been created successfully. Below are your login details:

        Email: {self.email}
        Password: {plain_password}

        Best regards,
        Research Coordination Office
        """
        send_mail(
            subject,
            message,
            'smwondha@miu.ac.ug',
            [self.email],
            fail_silently=False,
        )


class Position(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    votes = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='candidate_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.position.title}"

    def get_vote_count(self):
        """Returns the count of votes for this candidate."""
        return Vote.objects.filter(candidate=self).count()


class Vote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'candidate')

    def __str__(self):
        return f"{self.student.name} voted for {self.candidate.name} in {self.candidate.position.title}"


@receiver(post_save, sender=Student)
def send_voter_update_email(sender, instance, **kwargs):
    if instance.is_active and not instance.has_voted:
        subject = "Your Voting Status Update"
        message = f"""
        Dear {instance.name},

        Your registration as a voter has been approved successfully. You can now log in to vote.
        Check your email for login details.

        Best regards,
        Research Coordination Office
        """

        send_mail(
            subject,
            message,
            'smwondha@miu.ac.ug',
            [instance.email],
            fail_silently=False,
        )
