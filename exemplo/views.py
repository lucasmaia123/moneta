from django.shortcuts import render
import pyrebase
from django.utils import timezone
from firebase_admin import storage as admin_storage, credentials, initialize_app as admin_app
import json
from pathlib import Path
import os

# Credenciais do Firebase na minha conta
# Você pode acessar as credenciais da sua conta nas configurações do Firebase
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

# Bullshit necessário para guardar estáticos no Firebase
storage = firebase.storage()
dir = Path(__file__).resolve().parent.parent
# Você vai ter que baixar as configurações da sua conta no site do Firebase em 'gerar chave privada'
# para fazer download do json com as credenciais
dir = os.path.join(dir, "monetadb-a221d-firebase-adminsdk-dilx3-44c3d27db3.json")
cred = credentials.Certificate(json.load(open(dir)))
# Utilize a URL do seu Storage
admin_app(cred, {"storageBucket": "monetadb-a221d.appspot.com"})

def index(request):
    # Página inicial
    # Acessa os cookies para ver se alguem já está logado nesta máquina
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
    # Renderiza uma página HTML
    return render(request, 'index.html', context)

def login_page(request):
    # Mesmo da página inicial
    try:
        idToken = request.session['uid']
        email = authe.get_account_info(idToken)
        email = email['users'][0]['email']
        return render(request, 'user.html', {'email': email})
    except:
        pass
    return render(request, 'login.html')

def user_page(request):
    # Recebe credenciais por formulário HTML e tenta logar o usuário
    # Caso conta exista, redireciona para página do usuário
    # Pode implementar por API utilizando POST
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
    # Deleção de cookies
    try:
        del request.session['uid']
    except KeyError:
        pass
    return render(request, 'login.html')

def SignUp(request):
    # Apenas um redirecionamento para fazer uso da função render
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
    # Status era para implementar um sistema para ver quais usuários estão logados
    # mas eu nunca fiz, sinta-se livre para não usar

    database.child('users').child(uid).child('details').set(data)
    message = "Account created sucessfully!"
    return render(request, 'login.html', context={"msg": message})

def create_redirect(request):
    return render(request, 'create.html')

def create_post(request):
    # Esta função é chamada por um formulário HTML
    title = request.POST.get('title')
    description = request.POST.get('description')
    try:
        # Guardando um estático no Firebase
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
    # Pega o horário atual para identificar o post
    date = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = authe.get_account_info(idToken)
    email = user_id['users'][0]['email']
    user_id = user_id['users'][0]['localId']

    # Insere os dados no Firebase
    database.child('users').child(user_id).child('posts').child(date).set(data)
    return render(request, "user.html", context={'email': email})

def check(request):
    try:
        idToken = request.session['uid']
    except KeyError:
        message = "Session terminated, please log in again!"
        return render(request, 'login.html', context={"msg": message})
    user_id = authe.get_account_info(idToken)
    user_id = user_id['users'][0]['localId']

    timestamps = database.child('users').child(user_id).child('posts').shallow().get().val()
    if timestamps == None:
        message = "Usuário não possui relatórios!"
        return render(request,'user.html', context={"msg": message})
    
    # Converte o dicionário em lista
    # print(timestamps)
    times = []
    for i in timestamps:
        times.append(i)
    titles = []
    for i in times:
        title = database.child('users').child(user_id).child('posts').child(i).child('title').get().val()
        titles.append(title)

    # Combina os dados e envia para a página
    post_info = zip(times, titles)
    name = database.child('users').child(user_id).child('details').child('name').get().val()
    return render(request, 'check.html', context={"post_info": post_info, "name": name})

def post_check(request):
    # Pega a variável z direto do URL (Implementado no check.html)
    date = request.GET.get('z')

    try:
        idToken = request.session['uid']
    except KeyError:
        message = "Session terminated, please log in again!"
        return render(request, 'login.html', context={"msg": message})
    user_id = authe.get_account_info(idToken)
    user_id = user_id['users'][0]['localId']

    title = database.child('users').child(user_id).child('posts').child(date).child('title').get().val()
    description = database.child('users').child(user_id).child('posts').child(date).child('description').get().val()
    try:
        # Acessa o arquivo estático no Storage atraves do URL guardado no banco de dados
        imgURL = database.child('users').child(user_id).child('posts').child(date).child('url').get().val()
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
    file = database.child('users').child(user_id).child('posts').child(date).child('file').get().val()
    try:
        # Deleta a postagem do banco de dados e do storage caso exista estático
        database.child('users').child(user_id).child('posts').child(date).remove()
        if file:
            bucket = admin_storage.bucket()
            blob = bucket.blob(file)
            blob.delete()
        return render(request, 'post_check.html', context={"msg": "Report deleted!"})
    except:
        return render(request, 'post_check.html', context={'msg': 'Error, could not delete'})