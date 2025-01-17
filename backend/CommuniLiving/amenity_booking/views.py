from django.shortcuts import render 
from rest_framework.views import APIView 
from . models import *
from rest_framework.response import Response 
from . serializers import *

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from rest_framework import status
from rest_framework.decorators import api_view


from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token

from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse
from datetime import date, timedelta, datetime


# Dummy view to test the connection between the frontend and the backend
# Feel free to edit this to test new api endpoints
class DummyView(APIView):
    authentication_classes = []  # No authentication
    permission_classes = [AllowAny]  # Allow any user to access
    # permission_classes = (IsAuthenticated, )
    def get(self, request):
        # Example of returning a simple JSON response
        dummy_data = {
            "key": "value",
            "text": "This is to test the connection between the frontend and the backend."
        }
        return Response(dummy_data)

    def post(self, request):
        pass

# class AmenitiesView(APIView):
#     """Returns a list of all amenities in the database for the given shared space."""
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     permission_classes = [AllowAny]

#     def get(self, request, community_id=None):
#         if community_id:
#             amenities = Amenity.objects.filter(community__id=community_id) # return amenities for the given shared space
#         else:
#             amenities = Amenity.objects.all() # return all amenities in the database
#         serializer = AmenitySerializer(amenities, many=True)  # Serialize the queryset
#         return Response(serializer.data)

# class TimeTableView(APIView):
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     permission_classes = [AllowAny]

#     def get(self, request, amenity_id=None):
#         """Returns all bookings for a specific day."""
#         curr_date = str(date.today()-timedelta(days=2))
#         print(curr_date)
#         # if 'date' not in request.query_params:
#         #     return Response({"error": "Date parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

#         # try:
#         #     date = parse_date(request.query_params['date'])
#         # except ValueError:
#         #     return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

#         if amenity_id:
#             bookings = Booking.objects.filter(amenity=amenity_id, date=curr_date)
#         else:
#             user = request.user
#             bookings = Booking.objects.filter(date=curr_date)

#         serializer = BookingSerializer(bookings, many=True)
#         return Response(serializer.data)

# class MessageView(APIView):
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     permission_classes = [AllowAny]

#     def get(self, request, community_id=None):
#         """Returns all bookings for a specific day."""
#         # if 'community' not in request.query_params:
#         #     return Response({"error": "Community parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)

#         # try:
#         #     community = parse_date(request.query_params['community'])
#         # except ValueError:
#         #     return Response({"error": "Invalid community format"}, status=status.HTTP_400_BAD_REQUEST)
#         # community_id = 1

#         if community_id:
#             messages = Message.objects.filter(community=community_id)
#         else:
#             return Response({"error": "Community ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = MessageSerializer(messages, many=True)
#         return Response(serializer.data)

@csrf_exempt
def MessageView(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data['username']
            community_name = data['community_name']
            message = data['message']

            try:
                community = Community.objects.get(name=community_name)
            except Community.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Community not found'})
            
            user_profile = UserProfile.objects.get(user__username=username)
            user = user_profile.user

            if username and community and message:
                # curr_date = str(date.today())

                new_message = Message.objects.create(
                    user=user,
                    date=date.today(),
                    community=community,  # Assuming you want to associate the message with the first community
                    message=message
                )
                # return JsonResponse({'status': 'success', 'id': -1, 'community': community.name, 'user':username, 'date': date, 'message': message})
                formatted_date = new_message.date.strftime("%Y-%m-%d")

                return JsonResponse({
                    'status': 'success', 
                    'id': new_message.id, 
                    'community': community.name, 
                    'user': username, 
                    'date': formatted_date, 
                    'message': message
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Missing required data'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})

    if request.method == 'GET':
        try:
            # data = json.loads(request.body.decode('utf-8'))
            # username = data['username']
            username = request.GET.get('username')

            if username:
                user_profile = UserProfile.objects.get(user__username=username)
                user = user_profile.user
                user_communities = user_profile.get_communities()

                # Retrieve all communities for the user
                user_communities = user_profile.get_communities()

                # Retrieve messages for the user's communities
                messages = Message.objects.filter(community__in=user_communities)

                # print(messages)

                # Serialize messages
                message_data = [{'id': message.id, 'community': message.community.name, 'user': message.user.username, 'date': message.date.strftime("%Y-%m-%d"), 'message': message.message} for message in messages]
                
                # print(message_data)

                response_data = {'status': 'success', 'messages': message_data}
                response = JsonResponse(response_data)
                # response.set_cookie('csrftoken', get_token(request))
                # response.set_cookie('sessionid', request.session.session_key, httponly=False, secure=False)
                # response.set_cookie('username', user.username, httponly=False, secure=False)
                return response

        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User profile not found'})

        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

            


class BookingView(APIView): 

    serializer_class = BookingSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny] # [IsAuthenticated ] User must be authenticated to make a booking
  
    def get(self, request, amenity_id=None):
        """Returns a list of all bookings in the database for a user."""
        """Or Returns a list of all bookings in the database for the given amenity if amenity id is provided."""
        if amenity_id:
            bookings = Booking.objects.filter(amenity=amenity_id)
        else:
            user = request.user
            bookings = Booking.objects.filter(user=user.id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
  
    def post(self, request): 
        """ Creates a new booking in the database for an amenity."""
        print(request.user)
        # hard coding user for now, to be session authenticated later
        request.data['user'] = 1
        serializer = BookingSerializer(data=request.data)
        amenityId = request.data['amenity']
        date = request.data['date']
        start_time = request.data['start_time']
        end_time = request.data['end_time']

        if serializer.is_valid(raise_exception=True):
            print("serializer is valid")
            # print(serializer.validated_data)
            # check if the amenity is already booked
            if Booking.objects.filter(amenity__id=amenityId, date=date, start_time=start_time, end_time=end_time).exists():
                return Response("The amenity is already booked", status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

# @csrf_exempt
# def register_user(request):
#     print("here")
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
     permission_classes = (IsAuthenticated,)
     def post(self, request):
          
          try:
               refresh_token = request.data["refresh_token"]
               token = RefreshToken(refresh_token)
               token.blacklist()
               return Response(status=status.HTTP_205_RESET_CONTENT)
          except Exception as e:
               return Response(status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def LoginView(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data['username']
            password = data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Include additional user info in the response
                user_info = {
                    'username': user.username,
                    # Include other fields as needed
                    'email': user.email,
                    # etc.
                }
                response = JsonResponse({'status': 'success', 'user': user_info})
                response.set_cookie('csrftoken', get_token(request))
                print(request.session)
                response.set_cookie('sessionid', request.session, httponly=False, secure=False)
                response.set_cookie('username', user.username, httponly=False, secure=False)
                return response
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'success'})

@csrf_exempt
def user_info(request):
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username})
    else:
        return JsonResponse({'username': None})

# @csrf_exempt
# def register_user(request):
#     if request.method == 'POST':
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             email = form.cleaned_data.get('email')
#             password = form.cleaned_data.get('password')
#             User.objects.create_user(username=username, email=email, password=password)
#             return redirect('edit-profile')
#         else:
#             form = SignupForm()

#         context = {
#             'form':form,
#         }

#     return render(request, 'registration/signup.html', context)

@csrf_exempt
def AddUserCommunity(request):
    print("i am being called")
    if request.method == 'POST':
        print("i am being called")
        print(request.body)
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data['user']
            community_pass = data['community_pass']

            # username = 'thomas'
            # community_pass = '942767'

            try:
                # print(Community.objects.get(join_pass=091786))
                community = Community.objects.get(join_pass=community_pass)
            except Community.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid community pass'}, status=400)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)

            user_profile, created = UserProfile.objects.get_or_create(user=user)
            # user_profile.communities.add(community)
            # # user_profile.communities.remove(community)
            # print(user_profile.get_communities())

            if community not in user_profile.communities.all():
                user_profile.communities.add(community)
                print(user_profile.get_communities())
                return JsonResponse({'status': 'success', 'user_id': user.id}, status=201)
            else:
                return JsonResponse({'status': 'error', 'message': 'User is already part of the community'}, status=400)


            return JsonResponse({'status': 'success', 'user_id': user.id}, status=201)
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def SignupView(request):
    # data = json.loads(request.body.decode('utf-8'))
    data = request.data

    username = data['username']
    email = data['email']
    password = data['password']
    re_password = data['re_password']
    serializer = SignupSerializer(data=data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        re_password = serializer.validated_data['re_password']
    else:
        print("Validation errors:", serializer.errors)
        return Response({'error': 'Invalid data provided'}, status=status.HTTP_400_BAD_REQUEST)

    if password != re_password:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 6:
        return Response({'error': 'Password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)

    # Create the user profile
    user_profile = UserProfile.objects.create(user=user)

    # Return a success response
    return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

@csrf_exempt
def getUserCommunities(request):
    if request.method == 'GET':
        try:
            username = request.GET.get('username')
            # Boolean for if you want to return detailed information for communities
            details = request.GET.get('details')

            if username:
                user_profile = UserProfile.objects.get(user__username=username)
                user = user_profile.user
                user_communities = user_profile.get_communities()

                # Retrieve all communities for the user
                user_communities = user_profile.get_communities()

                if bool(details) == True:
                    community_data = [{'id': community.id, 'community_name': community.name, 'join_pass': community.join_pass, 'description': community.description, 'location': community.location} for community in user_communities]
                else:
                    community_data = [{'id': community.id, 'community_name': community.name} for community in user_communities]

                response_data = {'status': 'success', 'communities': community_data}
                response = JsonResponse(response_data)
                return response

        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User profile not found'})

        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


class TimeTableView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, community_id):
    # def get(self, request, community_id=1): # Use this for TESTING
        """Returns all bookings for a specific day with availability for 30-minute increments."""
        try:
            date_param = request.query_params.get('date')
            if date_param:
                curr_date = datetime.strptime(date_param, "%Y-%m-%d")
            else:
                curr_date = datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)

            amenities = Amenity.objects.filter(community=community_id)

            amenities_data = []

            for amenity in amenities:
                time_slots = []
                current_time = curr_date.replace(hour=0, minute=0, second=0, microsecond=0)

                while current_time < curr_date.replace(hour=23, minute=59):
                    end_time = current_time + timedelta(minutes=30)

                    # Check if the slot is booked
                    is_booked = Booking.objects.filter(
                        amenity=amenity,
                        date=curr_date.date(),
                        start_time__lt=end_time,
                        end_time__gt=current_time
                    ).exists()

                    time_slots.append({
                        'start_time': current_time.strftime("%H:%M"),
                        'end_time': end_time.strftime("%H:%M"),
                        'is_booked': is_booked
                    })

                    current_time = end_time

                amenities_data.append({
                    'amenity_name': amenity.name,  # Assuming your Amenity model has a 'name' field
                    'amenity_id': amenity.id,
                    'time_slots': time_slots
                })

            return Response({'date': curr_date.strftime("%Y-%m-%d"), 'amenities': amenities_data})

        except ValueError:
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

class AmenitiesView(APIView):
    def get(self, request, community_name):
        try:
            # Get the community based on the input name
            community = Community.objects.get(name=community_name)

            # Get all amenities associated with the community
            amenities = Amenity.objects.filter(community=community)

            # Serialize the amenities data
            amenity_data = [{'name': amenity.name, 'description': amenity.description} for amenity in amenities]

            return Response(amenity_data)

        except Community.DoesNotExist:
            return Response({'error': 'Community not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def createCommunity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            community_name = data['community_name']
            community_location = data['community_location']
            community_description = data['community_description']

            if community_name and community_location and community_description:

                Community.objects.create(
                    name=community_name,
                    location=community_location,
                    description=community_description
                )

                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Missing required data'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'})