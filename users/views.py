from django.shortcuts import render
import pyrebase
from django.utils import timezone
from firebase_admin import storage as admin_storage, credentials, initialize_app as admin_app
import json
from pathlib import Path
import os

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
storage = firebase.storage()
dir = Path(__file__).resolve().parent.parent
dir = os.path.join(dir, "monetadb-a221d-firebase-adminsdk-dilx3-44c3d27db3.json")
cred = credentials.Certificate(json.load(open(dir)))
admin_app(cred, {"storageBucket": "monetadb-a221d.appspot.com"})

def index(request):
    # Página inicial
    try:
        idToken = request.session['uid']
        user_id = authe.get_account_info(idToken)
        user_id = user_id['users'][0]['localId']
        user = database.child('users').child(user_id).child('details').child('name').get().val()
    except:
        user = None

    context = {
        'nome': user
    }
    return render(request, 'index.html', context)

def login_page(request):
    try:
        idToken = request.session['uid']
        email = authe.get_account_info(idToken)
        email = email['users'][0]['email']
        return render(request, 'user.html', {'email': email})
    except:
        pass
    return render(request, 'login.html')

def user_page(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
        user = authe.sign_in_with_email_and_password(email, password)
    except:
        message = "Invalid credentials!"
        return render(request, 'login.html', {"msg": message})
    # Cria um indentificador para o usuário logado utilizando o session do http
    session_id = user['idToken']
    request.session['uid'] = str(session_id)
    request.session.modified = True
    return render(request, 'user.html', {'email': email})

def logout(request):
    try:
        del request.session['uid']
    except KeyError:
        pass
    return render(request, 'login.html')

def SignUp(request):
    return render(request, 'signup.html')

def createuser(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
        user = authe.create_user_with_email_and_password(email, password)
    except:
        message = "Senha fraca, utilize pelo menos 6 digitos!"
        return render(request, "signup.html", context={"msg": message})
    uid = user['localId']
    data = {"name": name, "status": "1"}

    database.child('users').child(uid).child('details').set(data)
    message = "Account created sucessfully!"
    return render(request, 'login.html', context={"msg": message})

def create_redirect(request):
    return render(request, 'create.html')

def create_post(request):
    # Esta função é chamada por um formulário com metodo POST
    title = request.POST.get('title')
    description = request.POST.get('description')
    try:
        file = request.FILES['file']
        storage.child(file.name).put(file)
        url = storage.child(file.name).get_url(None)
        f_name = file.name
    except:
        url = None
        f_name = None

    data = {
        "title": title,
        "description": description,
        "url": url,
        "file": f_name
    }
    # Pega o Id do usuário logado
    try:
        idToken = request.session['uid']
    except KeyError:
        message = "Session terminated, please log in again!"
        return render(request, 'login.html', context={"msg": message})
    # Pega o horário atual para classificar o relatório
    date = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    print(date)
    user_id = authe.get_account_info(idToken)
    user_id = user_id['users'][0]['localId']
    print(user_id)

    # Insere os dados no Firebase
    database.child('users').child(user_id).child('reports').child(date).set(data)
    return render(request, "user.html")

def check(request):
    try:
        idToken = request.session['uid']
    except KeyError:
        message = "Session terminated, please log in again!"
        return render(request, 'login.html', context={"msg": message})
    user_id = authe.get_account_info(idToken)
    user_id = user_id['users'][0]['localId']

    timestamps = database.child('users').child(user_id).child('reports').shallow().get().val()
    if timestamps == None:
        message = "Usuário não possui relatórios!"
        return render(request,'user.html', context={"msg": message})
    
    '''
    # my query
    for key, value in timestamps.items():
        print(key, value)
    return render(request, 'user.html')
    '''
    # Converte o dicionário em lista
    times = []
    for i in timestamps:
        times.append(i)
    titles = []
    for i in times:
        title = database.child('users').child(user_id).child('reports').child(i).child('title').get().val()
        titles.append(title)

    # Combina os dados e envia para a página
    post_info = zip(times, titles)
    name = database.child('users').child(user_id).child('details').child('name').get().val()
    return render(request, 'check.html', context={"post_info": post_info, "name": name})

def post_check(request):
    # Pega a variável z direto do URL
    date = request.GET.get('z')

    try:
        idToken = request.session['uid']
    except KeyError:
        message = "Session terminated, please log in again!"
        return render(request, 'login.html', context={"msg": message})
    user_id = authe.get_account_info(idToken)
    user_id = user_id['users'][0]['localId']

    title = database.child('users').child(user_id).child('reports').child(date).child('title').get().val()
    description = database.child('users').child(user_id).child('reports').child(date).child('description').get().val()
    try:
        imgURL = database.child('users').child(user_id).child('reports').child(date).child('url').get().val()
    except:
        pass
    return render(request, 'post_check.html', context={"t": title, "d": description, "i": imgURL, "dt": str(date)})

def post_delete(request, date):
    try:
        idToken = request.session['uid']
    except KeyError:
        message = "Session terminated, please log in again!"
        return render(request, 'login.html', context={"msg": message})
    user_id = authe.get_account_info(idToken)
    user_id = user_id['users'][0]['localId']
    file = database.child('users').child(user_id).child('reports').child(date).child('file').get().val()
    try:
        database.child('users').child(user_id).child('reports').child(date).remove()
        if file:
            bucket = admin_storage.bucket()
            blob = bucket.blob(file)
            blob.delete()
        return render(request, 'post_check.html', context={"msg": "Report deleted!"})
    except:
        return render(request, 'post_check.html', context={'msg': 'Error, could not delete'})