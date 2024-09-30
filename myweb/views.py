from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .models import Student, Candidate, Position, Vote
from .forms import StudentForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count


from datetime import datetime
from django.shortcuts import render
from django.db.models import Count
from .models import Candidate

def home(request):
    # Get all candidates grouped by their positions
    candidates = Candidate.objects.select_related('position').annotate(vote_count=Count('vote'))

    # Group candidates by position
    positions_with_candidates = {}
    for candidate in candidates:
        position_title = candidate.position.title  # Assuming your Position model has a 'title' field
        if position_title not in positions_with_candidates:
            positions_with_candidates[position_title] = []
        positions_with_candidates[position_title].append(candidate)

    return render(request, 'home.html', {
        'positions_with_candidates': positions_with_candidates,
        'year': datetime.now().year,
    })





def register(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        if student_form.is_valid():
            student = student_form.save()
            messages.success(request, "Registration successful. Please check your email for login details.")
            return redirect('login')  # Redirect to login page after successful registration
    else:
        student_form = StudentForm()

    return render(request, 'register.html', {'student_form': student_form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            reg_no = form.cleaned_data['reg_no']
            password = form.cleaned_data['password']
            student = authenticate(request, reg_no=reg_no, password=password)
            if student is not None:
                login(request, student)
                return redirect('vote')
            else:
                form.add_error(None, "Invalid registration number or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Candidate, Position, Vote

@login_required
def vote(request):
    student = request.user  # Assuming you're using a custom user model for students

    # Retrieve all the votes the student has already cast
    votes = Vote.objects.filter(student=student)

    # Create a set of positions the student has already voted for
    voted_positions = set(vote.candidate.position for vote in votes)

    # Handle the POST request when the form is submitted
    if request.method == 'POST':
        selected_candidates = {}

        for position in Position.objects.all():
            candidate_id = request.POST.get(f'position_{position.id}')
            if candidate_id:
                # Check if the student has already voted for this position
                if position in voted_positions:
                    messages.error(request, f"You have already voted for the position: {position.title}.")
                    return redirect('vote')

                # Create a Vote entry
                candidate = Candidate.objects.get(id=candidate_id)
                Vote.objects.create(student=student, candidate=candidate)
                voted_positions.add(position)  # Add this position to voted_positions to prevent double voting

        messages.success(request, "Your vote has been successfully cast!")
        return redirect('success')  # Redirect to results or any appropriate page

    candidates = Candidate.objects.all()
    positions = Position.objects.all()

    return render(request, 'vote.html', {
        'candidates': candidates,
        'positions': positions,
        'student': student,
        'voted_positions': voted_positions,
    })



from django.shortcuts import render
from django.db.models import Count
from .models import Candidate, Student

def success(request):
    # Get all candidates along with their positions and vote counts
    candidates = Candidate.objects.select_related('position').annotate(vote_count=Count('vote'))

    # Create a dictionary to group candidates by their positions
    positions_with_candidates = {}
    for candidate in candidates:
        position_title = candidate.position.title  # Assuming your Position model has a 'title' field
        if position_title not in positions_with_candidates:
            positions_with_candidates[position_title] = {'candidates': [], 'total_votes': 0}
        positions_with_candidates[position_title]['candidates'].append(candidate)
        positions_with_candidates[position_title]['total_votes'] += candidate.vote_count

    # Count total registered students and total votes
    total_students = Student.objects.count()  # Count of registered students
    total_votes = sum(candidate.vote_count for candidate in candidates)  # Sum of all votes

    return render(request, 'success.html', {
        'positions_with_candidates': positions_with_candidates,
        'total_students': total_students,
        'total_votes': total_votes,
    })
