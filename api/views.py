from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import pyrebase
import datetime
import yfinance as yf
from pandas import Series
import pmdarima as pm

# Credenciais do Firebase
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

# Treina um modelo baseado em 200 dias com sazonalidade 4
# Quanto maior o número de dias e sazonalidade, mais demorado fica o treinamento
# Você pode guardar os modelos no banco de dados para não ter que treinar um ticker denovo
# tambem recomendo colocar isso em uma thread para casos em que está treinando múltiplos tickers, boa sorte...
def train_model(ticker):
    e = datetime.datetime.now()
    s = (e - datetime.timedelta(200)).strftime('%Y-%m-%d')
    e = e.strftime('%Y-%m-%d')
    data = yf.download(ticker, start=s, end=e)
    data = data.reset_index()
    data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
    data = Series(data['Close'])
    data = data.resample('D').interpolate()
    model = pm.ARIMA((1,1,1), (1, 1, 1, 4))
    model = model.fit(data)
    return model

# Ferramenta da API utilizando decorators para views baseados em funções
@api_view(['GET', 'POST'])
def stock_predict(request):
    if request.method == 'POST':
        data = request.data
        tickers = data['tickers']
        period = data['period']
        predictions = {}
        for ticker in tickers:
            try:
                model = train_model(ticker)
            except:
                continue
            prediction = model.predict(period)
            date = datetime.datetime.now()
            prediction_aux = []
            for value in prediction:
                aux = {}
                aux['Date'] = date.strftime('%Y-%m-%d')
                aux['Close'] = value
                prediction_aux.append(aux)
                date = date + datetime.timedelta(1)
            predictions[ticker] = prediction_aux
        return Response(predictions)
    else:
        message = {"Instruções": "Mande as credenciais em 'tickers' no formato de lista ['cred1', 'cred2'] e o número de dias a serem previstos em 'period'"}
        return Response(message) 

# Pega os dados da bolsa sem predição
@api_view(['GET', 'POST'])
def stock_info(request):
    if request.method == 'POST':
        data = request.data
        tickers = data['tickers']
        period = data['period']
        e = datetime.datetime.now()
        s = (e - datetime.timedelta(period)).strftime('%Y-%m-%d')
        e = e.strftime('%Y-%m-%d')
        stocks = {}
        for ticker in tickers:
            try:
                stock = yf.download(ticker, start=s, end=e)['Close']
                stock_aux = []
            except:
                print(f"Failed to collect data of {ticker}\n")
                continue
            for date, value in stock.items():
                aux = {}
                aux['Date'] = date.date()
                aux['Close'] = value
                stock_aux.append(aux)
            stocks[ticker] = stock_aux
        return Response(stocks)
    else:
        message = {"Instruções": "Mande as credenciais em 'tickers' no formato de lista ['cred1', 'cred2'] e o número de dias para coleta em 'period'"}
        return Response(message)

# Loga o usuário com autenticação do Firebase
@api_view(['GET', 'POST'])
def login_user(request):
    if request.method == 'POST':
        data = request.data
        email = data['email']
        password = data['senha']
        try:
            user = authe.sign_in_with_email_and_password(email, password)
            return Response([status.HTTP_202_ACCEPTED, {"user": user}])
        except:
            error = "Credenciais invalidas!"
            return Response([status.HTTP_406_NOT_ACCEPTABLE, {'error': error}])
    else:
        message = "Mande o email e senha do usuário em 'email' e 'senha'"
        return Response({'instruções': message})

# Cria uma conta com autenticação do Firebase
@api_view(['GET', 'POST'])
def signup(request):
    if request.method == 'POST':
        data = request.data
        email = data['email']
        password = data['senha']
        try:
            user = authe.create_user_with_email_and_password(email, password)
            return Response([status.HTTP_201_CREATED, {'user': user}])
        except:
            error = "Algo deu errado, verifique se a senha possui pelo menos 6 caracteres ou se o usuário já existe!"
            return Response([status.HTTP_406_NOT_ACCEPTABLE, {"error": error}])
    else:
        message = "Mande o email e senha do usuário em 'email' e 'senha'"
        return Response({'instruções': message})

# Página inicial
@api_view(['GET'])
def index(request):
    data = [{
        "endpoint": "users/",
        "metodo": "GET",
        "descrição": "Lista os nomes dos usuários cadastrados"
    },
    {
        "endpoint": "login/",
        "metodo": "POST",
        "instrução": "Mande o email e senha do usuário em 'email' e 'senha'",
        "descrição": "Loga  usuário com autenticação do Firebase"
    },
    {
        "endpoint": "signup/",
        "metodo": "POST",
        "instrução": "Mande o email e senha do usuário em 'email' e 'senha'",
        "descrição": "cria um usuário com autenticação do Firebase"
    },
    {
        "endpoint": "stocks/",
        "metodo": "POST",
        "instrução": "Mande as credenciais em 'tickers' no formato de lista ['cred1', 'cred2'] e o número de dias para coleta em 'period'",
        "descrição": "Lista os valores das ações em determinado período"
    },
    {
        "endpoint": "predict/",
        "metodo": "POST",
        "instrução": "Mande as credenciais em 'tickers' no formato de lista ['cred1', 'cred2'] e o número de dias previstos em 'period'",
        "descrição": "Manda os valores das ações previstos para os proximos dias"
    }]
    return Response({"Endpoints": data})

# Checa usuários criados
@api_view(['GET'])
def users(request):
    users = database.child('users').get().val()
    names = []
    for key in users:
        names.append(database.child('users').child(key).child('details').child('name').get().val())
    return Response({'Users': names})

# App de anotações para teste
# Checa anotações
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

# Cria uma anotação
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
    
# Deleta uma anotação
@api_view(['GET'])
def post_delete(request, id):
    try:
        database.child('notes').child(id).remove()
        return Response(status.HTTP_200_OK)
    except:
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)