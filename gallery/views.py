from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes
)

from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Artwork, Event
from .serializers import ArtworkSerializer, EventSerializer

from django.core.mail import send_mail
from django.contrib.auth.models import User

# 🎨 GET ARTWORKS (PUBLIC)
@api_view(['GET'])
def artwork_list(request):

    artworks = Artwork.objects.filter(is_visible=True)

    serializer = ArtworkSerializer(
        artworks,
        many=True
    )

    return Response(serializer.data)


# 🎨 UPLOAD ARTWORK (ADMIN ONLY)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_artwork(request):

    # 🔐 ADMIN CHECK
    if not request.user.is_staff:
        return Response(
            {"error": "Admin only"},
            status=403
        )

    # 🖼 IMAGE REQUIRED
    if not request.FILES.get('image'):
        return Response(
            {"error": "Image is required"},
            status=400
        )

    try:
        artwork = Artwork.objects.create(
            title=request.data.get('title', ''),
            description=request.data.get('description', ''),
            price=request.data.get('price') or None,
            image=request.FILES.get('image'),
            size=request.data.get('size', ''),
            material=request.data.get('material', ''),
            currency=request.data.get('currency', 'USD'),
            location=request.data.get('location', '')
        )

        return Response({
            "message": "Uploaded successfully",
            "id": artwork.id
        })

    except Exception as e:
        print("UPLOAD ERROR:", str(e))

        return Response(
            {"error": str(e)},
            status=500
        )


# 🗑 DELETE ARTWORK (ADMIN ONLY)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_artwork(request, id):

    # 🔐 ADMIN CHECK
    if not request.user.is_staff:
        return Response(
            {"error": "Admin only"},
            status=403
        )

    try:
        art = Artwork.objects.get(id=id)

        art.delete()

        return Response({
            "message": "Deleted successfully"
        })

    except Artwork.DoesNotExist:
        return Response(
            {"error": "Not found"},
            status=404
        )


# 📅 GET EVENTS (PUBLIC)
@api_view(['GET'])
def get_events(request):

    events = Event.objects.all().order_by('-created_at')

    serializer = EventSerializer(
        events,
        many=True
    )

    return Response(serializer.data)


# 📅 CREATE EVENT (ADMIN ONLY)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_event(request):

    # 🔐 ADMIN CHECK
    if not request.user.is_staff:
        return Response(
            {"error": "Admin only"},
            status=403
        )

    # VALIDATION
    if not request.data.get('title'):
        return Response(
            {"error": "Title is required"},
            status=400
        )

    if not request.data.get('date') or not request.data.get('time'):
        return Response(
            {"error": "Date and time are required"},
            status=400
        )

    try:
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():

            # ✅ SAVE EVENT
            event = serializer.save()

            # 📬 GET SUBSCRIBERS
            subscribers = User.objects.filter(
                profile__receive_updates=True
            ).exclude(email="")

            emails = [user.email for user in subscribers]

            # ✨ SEND EMAILS
            if emails:
                send_mail(
                    subject=f"New Morada Update: {event.title}",
                    message=f"""
A new update has been posted on Morada.

Title: {event.title}

Location: {event.location}

Date: {event.date}

Time: {event.time}

Description:
{event.description}

Visit Morada to explore more artworks and updates.
                    """,
                    from_email=None,
                    recipient_list=emails,
                    fail_silently=False,
                )

            return Response({
                "message": "Event created successfully"
            })

        return Response(
            serializer.errors,
            status=400
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=500
        )

# 🗑 DELETE EVENT (ADMIN ONLY)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_event(request, id):

    # 🔐 ADMIN CHECK
    if not request.user.is_staff:
        return Response(
            {"error": "Admin only"},
            status=403
        )

    try:
        event = Event.objects.get(id=id)

        event.delete()

        return Response({
            "message": "Event deleted"
        })

    except Event.DoesNotExist:
        return Response(
            {"error": "Not found"},
            status=404
        )


# 🔐 LOGIN
@api_view(['POST'])
def login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=401
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "token": str(refresh.access_token),
        "is_admin": user.is_staff,
        "username": user.username,
    })


# 📝 REGISTER
@api_view(['POST'])
def register(request):

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    receive_updates = request.data.get("receive_updates")

    # VALIDATION
    if not username or not email or not password:
        return Response(
            {"error": "All fields are required"},
            status=400
        )

    # USERNAME EXISTS
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=400
        )

    # EMAIL EXISTS
    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"},
            status=400
        )

    # CREATE USER
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password)
    )

    # SAVE SUBSCRIPTION OPTION
    user.profile.receive_updates = receive_updates == "true"
    user.profile.save()

    return Response({
        "message": "Account created successfully"
    })


from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def contact_message(request):
    name = request.data.get("name")
    email = request.data.get("email")
    message = request.data.get("message")

    if not name or not email or not message:
        return Response({"error": "All fields required"}, status=400)

    send_mail(
        subject=f"New Contact Message from {name}",
        message=f"""
Name: {name}
Email: {email}

Message:
{message}
        """,
        from_email=email,
        recipient_list=["moradamanage@gmail.com"],
        fail_silently=False,
    )

    return Response({"message": "Sent successfully"})    