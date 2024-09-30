from django.db import models
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    short_code = models.CharField(max_length=10, unique=True)
    facultyemail = models.EmailField(max_length=100)

    def __str__(self):
        return self.name

class Supervisor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class StudentManager(BaseUserManager):
    def create_user(self, reg_no, password=None, **extra_fields):
        if not reg_no:
            raise ValueError('The Registration Number field must be set')
        student = self.model(reg_no=reg_no, **extra_fields)
        student.set_password(password)
        student.save(using=self._db)
        return student

    def create_superuser(self, reg_no, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(reg_no, password, **extra_fields)

class Student(AbstractBaseUser, PermissionsMixin):
    LEVEL_CHOICES = [
        ('DEGREE', 'Degree'),
        ('DIPLOMA', 'Diploma'),
        ('NATIONAL_CERTIFICATE', 'National Certificate'),
    ]
    profile_image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # New phone number field
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='DEGREE')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, blank=True, null=True)
    selected_topic = models.ForeignKey('ResearchTopic', null=True, blank=True, on_delete=models.SET_NULL, related_name='selected_for')
    start_date = models.DateField(blank=True, null=True)
    graduation_date = models.DateField(blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)  # New password field

    def __str__(self):
        return f"{self.name} - {self.reg_no}"

    def save(self, *args, **kwargs):
        if not self.password:
            plain_password = get_random_string(length=6)  # Generate plain password
            self.password = make_password(plain_password)  # Hash the password before saving

            # Send the plain password via email
            self.send_password_email(plain_password)
        super(Student, self).save(*args, **kwargs)

    def send_password_email(self, plain_password):
        subject = "Your Research Account Details"
        message = f"""
        Dear {self.name},

        Your account has been created successfully. Below are your login details:

        Registration Number: {self.reg_no}
        Password: {plain_password}

        Please change your password upon first login.

        Best regards,
        Research Coordination Office
        """

        send_mail(
            subject,
            message,
            'smwondha@miu.ac.ug',  # Sender email
            [self.email],  # Recipient email
            fail_silently=False,
        )

class ResearchTopic(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200, unique=True)
    district_of_study = models.CharField(max_length=100)
    case_study_area = models.CharField(max_length=100)
    topic_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.topic

    def clean(self):
        # Ensure the topic is unique across all students
        if ResearchTopic.objects.exclude(id=self.id).filter(topic=self.topic).exists():
            raise ValidationError('This research topic has already been assigned to another student.')

class Milestone(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    milestone_name = models.CharField(max_length=100)
    due_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.selected_topic.topic} - {self.milestone_name}"

class Meeting(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    discussion_points = models.TextField()
    action_items = models.TextField()

    def __str__(self):
        return f"{self.student.selected_topic.topic} {self.date} {self.discussion_points}"

class ResearchFile(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='research_files/')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description if self.description else str(self.file)


@receiver(post_save, sender=Student)
def send_update_email(sender, instance, **kwargs):
    if instance.supervisor and instance.selected_topic and instance.start_date:
        # Calculate proposal, findings, and report deadlines
        proposal_deadline = instance.start_date + timedelta(days=30)  # 1 month after start date
        findings_deadline = proposal_deadline + timedelta(days=60)  # 2 months after proposal deadline
        report_deadline = findings_deadline + timedelta(days=30)  # 1 month after findings deadline
        defense_date = instance.graduation_date - timedelta(days=60)  # 2 months before graduation date

        subject = "Research Information Updated"
        message = f"""
        <div style="max-width: 600px; margin: auto; font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
            <div style="background-color: rgba(4, 71, 1, 0.973); padding: 10px; text-align: center; color: white;">
                <h2 style="margin: 0;">METROPOLITAN INTERNATIONAL UNIVERSITY</h2>
                <p>Research Coordination Office</p>
            </div>
            <div style="padding: 20px;">
                <p style="text-align: right;">Metropolitan International University</p>
                <p style="text-align: right;">P.O BOX 160, KISORO, UGANDA</p>
                <p style="text-align: right;">{instance.start_date.strftime('%Y-%m-%d')}</p>

                <p><strong>To:</strong> {instance.name}<br>
                {instance.reg_no}<br>
                {instance.email}</p>

                <p>Dear {instance.name},</p>
                <p>We are pleased to inform you that your research proposal has been reviewed and approved. Below are the details of your assigned research topic, supervisor, and the official start date of your research:</p>
                <p><strong>Research Topic:</strong> {instance.selected_topic.topic}<br>
                <strong>Supervisor:</strong> {instance.supervisor.name}<br>
                <strong>Start Date:</strong> {instance.start_date.strftime('%Y-%m-%d')}<br>
                <strong>Graduation Date:</strong> {instance.graduation_date.strftime('%Y-%m-%d')}</p>

                <p>Your research schedule is as follows:</p>
                <ul>
                    <li><strong>Proposal Submission Deadline:</strong> {proposal_deadline.strftime('%Y-%m-%d')}</li>
                    <li><strong>Findings Submission Deadline:</strong> {findings_deadline.strftime('%Y-%m-%d')}</li>
                    <li><strong>Final Report Deadline:</strong> {report_deadline.strftime('%Y-%m-%d')}</li>
                    <li><strong>Defense Date:</strong> {defense_date.strftime('%Y-%m-%d')}</li>
                </ul>

                <p>Please ensure that you adhere to the deadlines provided. If you have any questions or need further assistance, do not hesitate to contact your supervisor or the Research Coordination Office.</p>

                <p>Best regards,<br>
                Research Coordination Office<br>
                Metropolitan International University</p>
            </div>
        </div>
        """

        send_mail(
            subject,
            message,
            'smwondha@miu.ac.ug',  # Sender email
            [instance.supervisor.email],  # Recipient email
            html_message=message,
            fail_silently=False,
        )


        # Send email to the supervisor
        supervisor_subject = f"New Student Assigned: {instance.name}"
        supervisor_message = f"""
        <html>
            <head>
                <style>
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    th, td {{
                        border-bottom: 1px solid #ddd;
                        padding: 5px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f4f4f4;
                    }}
                    tr:nth-child(even) {{
                        background-color: #e6f7ff; /* Light blue */
                    }}
                    tr:nth-child(odd) {{
                        background-color: #f9f9f9; /* Pale white */
                    }}
                    div {{
                        max-width: 600px;
                        margin: auto;
                        -family: Arial, sans-serif;
                        border-radius: 10px;
                        overflow: hidden;
                    }}
                </style>
            </head>
            <body>
                <p>Dear {instance.supervisor.name},</p>
                <p>You have been assigned as the supervisor for the following student:</p>
                <div>
            <table>
                        <thead>
                            <tr>
            <th>Attribute</th>
                                <th>Details</th>
                            </tr>
                        </thead>
            <tbody>
            <tr>
                                <td>Student Name</td>
                                <td>{instance.name}</td>
            </tr>
            <tr>
            <td>Registration Number</td>
                                <td>{instance.reg_no}</td>
                            </tr>
            <tr>
            <td>Email</td>
            <td>{instance.email}</td>
                            </tr>
                            <tr>
                                <td>Research Topic</td>
                                <td>{instance.selected_topic.topic}</td>
            </tr>
                        </tbody>
                    </table>
                </div>
                <p>Please ensure you communicate with the student regularly and guide them through their research according to the timeline.</p>
                <p>Best regards,<br>
                Research Coordination Office</p>
            </body>
            </html>
            """

        send_mail(
            supervisor_subject,
            'Please view this email in HTML format.',  # Plain text fallback
        'smwondha@miu.ac.ug',  # Sender email
            [instance.supervisor.email],  # Supervisor's email
            fail_silently=False,
            html_message=supervisor_message  # HTML content
        )

# @receiver(post_save, sender=ResearchTopic)
# def notify_faculty_on_topic_submission(sender, instance, **kwargs):
#     if not instance.topic_approved:
#         student = instance.student
#         faculty = student.faculty
#         subject = "New Research Topic Submitted for Approval"
#         message = f"""
#         Dear {faculty.name} Faculty,

#         The following student has submitted a research topic that requires approval and supervisor assignment:

#         Student Name: {student.name}
#         Registration Number: {student.reg_no}
#         Email: {student.email}
#         Research Topic: {instance.topic}

#         Please take the necessary steps to review the topic and assign a supervisor.

#         Best regards,
#         Research Coordination Office
#         """

#         send_mail(
#             subject,
#             message,
#             'smwondha@miu.ac.ug',  # Sender email
#             [faculty.facultyemail],  # Faculty email
#             fail_silently=False,
#         )

#         # Notify the student of successful topic submission
#         student_subject = "Research Topic Submission Confirmation"
#         student_message = f"""
#         Dear {student.name},

#         Your research topic has been successfully submitted for review. The Research Coordination Office will review your topic and get back to you within 7 days.

#         Submitted Research Topic: {instance.topic}

#         Please ensure that you are available for any further communication during this review period.

#         Best regards,
#         Research Coordination Office
#         """

#         send_mail(
#             student_subject,
#             student_message,
#             'smwondha@miu.ac.ug',  # Sender email
#             [student.email],  # Student email
#             fail_silently=False,
#         )
