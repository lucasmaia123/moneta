from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import pyrebase

config = {
    "apiKey": "AIzaSyBgU1f7WYgfl5RjUXJQefju6bzwug9MqgI",
    "authDomain": "monetadb-a221d.firebaseapp.com",
    "databaseURL": "https://monetadb-a221d-default-rtdb.firebaseio.com/",
    "projectId": "monetadb-a221d",
    "storageBucket": "monetadb-a221d.appspot.com",
    "messagingSenderId": "138148189580",
    "appId": "1:138148189580:web:7c85454a34d9bf8665f2a9",
    "measurementId": "G-X6ZND3NKYV"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

@api_view(['GET'])
def index(request):
    data = {"Check users names": "/users/",
            "Check all notes or specific note": "/notes/<id>",
            "Post a new note": "/post_note/",
            "Delete a note": "/delete/<id>"
        }
    return Response({"Add the suffix to the URL": data})

@api_view(['GET'])
def users(request):
    users = database.child('users').get().val()
    names = []
    for key in users:
        names.append(database.child('users').child(key).child('details').child('name').get().val())
    return Response({'Users': names})

@api_view(['GET'])
def notes(request, id=None):
    if id:
        data = database.child('notes').child(id).get().val()
        return Response({'Note': data})
    else:
        id = database.child('notes').shallow().get().val()
        data = []
        for key in id:
            data.append({str(key):database.child('notes').child(key).get().val()})
        return Response({'Notes': data})

@api_view(['POST'])
def post_note(request):
    try:
        id = database.child('notes').shallow().get().val()
        id = len(id) + 1
    except:
        id = 1
    try:
        database.child('notes').child(id).set(request.data)
        return Response(status.HTTP_201_CREATED)
    except:
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def post_delete(request, id):
    try:
        database.child('notes').child(id).remove()
        return Response(status.HTTP_200_OK)
    except:
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)