import json
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, FileResponse
from .forms import StudentForm, ExcelGenerationForm
from face_recognition_app.models import Student
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime
import calendar
import pandas as pd
import os
from . import whatsapp_auto as kit
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def add_face(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            rno = form.cleaned_data['rno']
            stream = form.cleaned_data['stream']
            std = form.cleaned_data['std']
            mobile = form.cleaned_data['mobile']

            # Save the student record to the database
            student = Student.objects.create(name=name, rno=rno, stream=stream, std=std, mobile=mobile)
            return JsonResponse({'message': 'Student added successfully'})
        else:
            return JsonResponse({'error': 'Form is not valid'}, status=400)
    else:
        form = StudentForm()

    return render(request, 'add_face.html', {'form': form})


# views.py

from django.shortcuts import render
from .models import Student  # Assuming Student model is imported

def check(request):
    # Get query parameters from request
    query = request.GET.get('q')
    stream_filter = request.GET.get('stream')
    std_filter = request.GET.get('std')

    # Fetch distinct values for stream and std
    streams = Student.objects.order_by().values_list('stream', flat=True).distinct()
    stds = Student.objects.order_by().values_list('std', flat=True).distinct()

    # Filter students based on search query
    students = Student.objects.all()
    
    if query:
        students = students.filter(name__icontains=query)
    
    # Filter students based on stream and std if provided
    if stream_filter:
        students = students.filter(stream=stream_filter)
    if std_filter:
        students = students.filter(std=std_filter)
    
    # Pagination
    paginator = Paginator(students, 10)   # Show 10 students per page

    page_number = request.GET.get('page')
    try:
        students = paginator.page(page_number)
    except PageNotAnInteger:
        students = paginator.page(1)
    except EmptyPage:
        students = paginator.page(paginator.num_pages)
    
    return render(request, 'check.html', {'students': students, 'streams': streams, 'stds': stds})


def conv_pdf(request):
    excel_folder = os.path.join(settings.MEDIA_ROOT, 'excel_files')
    excel_files = []

    if os.path.exists(excel_folder):
        for file_name in os.listdir(excel_folder):
            if file_name.endswith('.xlsx'):
                file_path = os.path.join(excel_folder, file_name)
                excel_files.append({
                    'name': file_name,
                    'path': file_path,
                    'url': os.path.join(settings.MEDIA_URL, 'excel_files', file_name)
                })

    return render(request, 'conv_pdf.html', {'excel_files': excel_files})

def get_student_status_for_day(student, day):
    # Your logic to retrieve the status for the given day
    # For demonstration purposes, I'm returning a placeholder value "A" (Absent)
    return "A"


def generate_excel(request):
    if request.method == 'POST':
        form = ExcelGenerationForm(request.POST)
        if form.is_valid():
            stream = form.cleaned_data['stream']
            std = form.cleaned_data['std']

            # Filter records based on selected options
            students = Student.objects.filter(stream=stream, std=std)

            # Convert the queryset to a list
            students_list = list(students)

            # Create a DataFrame
            data = {
                'Rno': [student.rno for student in students_list],
                'Name': [student.name for student in students_list],
            }

            current_month_name = datetime.now().strftime("%B")
            current_year = datetime.now().year

            # Add columns for each day of the month
            for month in range(1, 13):
                _, last_day = calendar.monthrange(current_year, month)
                days_in_month = list(range(1, last_day + 1))

                for day in days_in_month:
                    day_column = f'{day}'
                    data[day_column] = [''] * len(students_list)

                    for student in students_list:
                        student_status = get_student_status_for_day(student, day)
                        data[day_column][students_list.index(student)] = student_status

            df = pd.DataFrame(data)

            # Generate Excel file
            excel_folder = os.path.join(settings.MEDIA_ROOT, 'excel_files')
            os.makedirs(excel_folder, exist_ok=True)

            excel_file_path = os.path.join(excel_folder, f'attendance_{stream}_{std}_{current_month_name}.xlsx')

            with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
                worksheet = writer.sheets['Sheet1']

                for col in range(2, len(df.columns) + 1):
                    worksheet.set_column(col, col, 2.50)

            response = FileResponse(open(excel_file_path, 'rb'))
            response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response['Content-Disposition'] = f'attachment; filename=attendance_{stream}_{std}_{current_month_name}.xlsx'

            return response
    else:
        form = ExcelGenerationForm()

    return render(request, 'generate_excel.html', {'form': form})


def update_excel(student, excel_file_path):
    try:
        df = pd.read_excel(excel_file_path)
    except FileNotFoundError:
        # If the Excel file doesn't exist, create it
        df = pd.DataFrame({
            'Rno': [],
            'Name': [],
        })

    # Get the current day
    current_day = datetime.now().day

    # Check if the column for the current day exists
    day_column = f'{current_day}'
    if day_column not in df.columns:
        df[day_column] = 'A'

    # Update status from 'A' to 'P' for the current day in the DataFrame
    df.loc[df['Name'] == student.name, day_column] = 'P'

    try:
        with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']

            for col in range(2, len(df.columns) + 1):
                worksheet.set_column(col, col, 2.50)

        return {'message': 'Excel file updated successfully'}
    except Exception as e:
        return {'error': str(e)}



def face_match(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

    current_day = datetime.now().day
    current_month_name = datetime.now().strftime("%B")

    excel_file_path = os.path.join(settings.MEDIA_ROOT, 'excel_files', f'attendance_{student.stream}_{student.std}_{current_month_name}.xlsx')

    if student.id == student_id:
        update_excel(student, excel_file_path)
        return JsonResponse({'message': 'Attendance updated successfully'})
    else:
        df = pd.read_excel(excel_file_path)
        current_day = date.today().day
        day_column = f'{current_day}'
        if day_column not in df.columns:
            df[day_column] = 'A'
        df.loc[df['Rno'] == student.rno, day_column] = 'A'
        with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']

            for col in range(2, len(df.columns) + 1):
                worksheet.set_column(col, col, 2.50)

        return JsonResponse({'message': 'Attendance marked as absent'})


def absent(request, id):
    stud = Student.objects.get(id=id)
    name = stud.name
    phone_number = stud.mobile

    message = f'Your child {name} is absent today...'

    kit.sendwhatmsg_instantly(f'{phone_number}', message)

    print(f"WhatsApp message sent successfully to {phone_number}")

    return redirect('/check')


    