from django.urls import path
from .views import *

urlpatterns = [
    path('', add_face, name='add_face'),
    path('check/', check, name='check'),
    path('conv_pdf/',conv_pdf, name='conv_pdf'),
    path('face_match/<int:student_id>/', face_match, name='face_match'),
    path('generate_excel/', generate_excel, name='generate_excel'),
    path('absent/<int:id>/', absent, name='absent'),
]