from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import pyrebase
import yfinance as yf

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

@api_view(['GET', 'POST'])
def stock_info(request):
    if request.method == 'POST':
        data = request.data
        tickers = data['tickers']
        period = data['period']
        stocks = []
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker).history(period)
                stocks.append({ticker:stock})
            except:
                print(f"Failed to collect data of {ticker}\n")
        return Response({"Stocks": stocks})
    else:
        message = '''Use POST para mandar as siglas das empresas em 'tickers' no formato de lista 
        e o periodo da coleta em 'period' na forma '<int>mo' para o número de meses '''
        return Response({'instruções': message})

@api_view(['GET', 'POST'])
def login_user(request):
    if request.method == 'POST':
        data = request.data
        email = data['email']
        password = data['password']
        try:
            user = authe.sign_in_with_email_and_password(email, password)
            return Response([status.HTTP_202_ACCEPTED, {"user": user}])
        except:
            error = "Credenciais invalidas!"
            return Response([status.HTTP_406_NOT_ACCEPTABLE, {'error': error}])
    else:
        message = "Use POST para mandar o email e senha na forma 'email' e 'password'"
        return Response({'instruções': message})

@api_view(['GET', 'POST'])
def signup(request):
    if request.method == 'POST':
        data = request.data
        email = data['email']
        password = data['password']
        try:
            user = authe.create_user_with_email_and_password(email, password)
            return Response([status.HTTP_201_CREATED, {'user': user}])
        except:
            error = "Algo deu errado, verifique se a senha possui pelo menos 6 caracteres ou se o usuário já existe!"
            return Response([status.HTTP_406_NOT_ACCEPTABLE, {"error": error}])
    else:
        message = "Use POST para mandar o email e senha na forma 'email' e 'password'"
        return Response({'instruções': message})


@api_view(['GET'])
def index(request):
    data = {"Checar nomes de usuários": "users/",
            "Logar em uma conta": "login/",
            "Criar uma conta": "signup/",
            "Pegar dados do mercado de ações": "stock/",
            "Checar uma ou varias anotações": "notes/<id>/",
            "Criar uma anotação": "post_note/",
            "Deletar uma anotação": "delete/<id>/"
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