from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Train, Booking
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import qrcode

# REGISTER
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password1')
        User.objects.create_user(username=username, password=password)
        return redirect('login')
    return render(request, 'reservation/register.html')


# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'reservation/login.html')


# DASHBOARD
@login_required
def dashboard(request):
    trains = Train.objects.all()
    return render(request, 'reservation/dashboard.html', {'trains': trains})


# BOOK TRAIN
@login_required
def book_train(request, train_id):
    train = get_object_or_404(Train, id=train_id)

    if request.method == "POST":
        travel_date = request.POST['travel_date']

        if train.seats > 0:
            Booking.objects.create(
                user=request.user,
                train=train,
                travel_date=travel_date
            )
            train.seats -= 1
            train.save()

        return redirect('mybookings')

    return render(request, 'reservation/book.html', {'train': train})


# CANCEL BOOKING
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.train.seats += 1
    booking.train.save()
    booking.delete()
    return redirect('mybookings')


# MY BOOKINGS
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'reservation/mybookings.html', {'bookings': bookings})


@login_required
def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>INDIAN RAILWAYS E-TICKET</b>", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))


    journey_data = [
        ["PNR", "Train No / Name", "Class"],
        [
            str(booking.id),
            f"{booking.train.train_number} / {booking.train.name}",
            "SLEEPER CLASS (SL)"
        ],
        ["From", "To", "Travel Date"],
        [
            booking.train.source,
            booking.train.destination,
            str(booking.travel_date)
        ],
    ]

    journey_table = Table(journey_data, colWidths=[2*inch, 2.5*inch, 2*inch])
    journey_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('BACKGROUND', (0,2), (-1,2), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    elements.append(journey_table)
    elements.append(Spacer(1, 0.4 * inch))

    passenger_data = [
        ["#", "Name", "Age", "Gender", "Status"],
        ["1", booking.user.username, "30", "F", "CONFIRMED"],
    ]

    passenger_table = Table(passenger_data, colWidths=[0.5*inch, 2*inch, 1*inch, 1*inch, 1.5*inch])
    passenger_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    elements.append(Paragraph("<b>Passenger Details</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(passenger_table)
    elements.append(Spacer(1, 0.4 * inch))

    payment_data = [
        ["Ticket Fare", f"₹ {booking.train.price}"],
        ["IRCTC Convenience Fee", "₹ 20.00"],
        ["Total Fare", f"₹ {booking.train.price + 20}"],
    ]

    payment_table = Table(payment_data, colWidths=[3*inch, 2*inch])
    payment_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
    ]))

    elements.append(Paragraph("<b>Payment Details</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.4 * inch))

    qr = qrcode.make(f"Ticket ID: {booking.id}, Passenger: {booking.user.username}")
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_image = Image(qr_buffer, 2*inch, 2*inch)
    elements.append(qr_image)

    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph("Beware of fraudulent customer care numbers.", styles['Normal']))
    elements.append(Paragraph("Thank you for booking with Indian Railways.", styles['Normal']))

    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
    return response


def logout_view(request):
    logout(request)
    return redirect('login')