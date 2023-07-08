Segue a api e um exemplo de site em HTML pra dar uma ideia de como fazer no Flutter
As configurações ficam na pasta 'moneta', recomendo que não mexa no settings
Para alterar os endpoints utilize os arquivos 'urls' dos respectivos aplicativos, mais informações em comentários no código

-- Passos iniciais --
1 - Crie um ambiente virtual indo no cmd ou powershell com o comando 'python -m venv venv', isto vai criar uma pasta chamada venv com uma cópia do interpretador do python.
Não é necessário para testes locais mas quando for instânciar em um servidor web, o aplicativo precisa estar encapsulado no seu ambiente virtual,
então, já crie um e coloque os arquivos dentro.

2 - Utilize o VScode ou o PyCharm para auxiliar no processo.
No VScode vc vai em select interpreters e seleciona o arquivo no venv em Scripts/python,
isso diz para a IDE utilizar o interpretador Python do venv.
(Caso queira utilizar o python do venv sem a IDE, você pode ativá-lo utilizando o comando './Scripts/activate' na pasta do venv)

3 - Abra um prompt de comando na IDE e digite 'pip install -r requirements.txt' para instalar os módulos necessários.

4 - Para testar se está tudo certo, no prompt de comando, navegue para a pasta inicial do moneta (aonde está o arquivo manage.py)
e digite 'python manage.py check'.



Para instânciar o servidor na sua máquina local, direcione o prompt de comando para a pasta inicial no moneta e digite o comando 'python manage.py runserver'.

Sempre que quiser passar alguma imagem para o aplicativo vc usa o comando 'python manage.py collectstatic' para gerar os estáticos na pasta static.
Já está feito para este exemplo.

O aplicativo deve estar rodando no domínio 127.0.0.1 ou localhost:8000,
nesse ponto apenas a sua máquina pode acessar o aplicativo, para jogá-lo na web você deve, ou instânciar o seu pc como um servidor web utilizando Apache ou nginx,
ou utilizar um serviço de deployment online, como o Railway ou o Heroku.

O aplicativo já está configurado para ser instanciado no Railway, basta colocá-lo no Github, criar uma conta no Railway e selecionar o repósitorio do aplicativo
que o Railway já toma conta de tudo.

Se estiver utilizando uma versão do python diferente de 3.10.6, coloque a versão utilizada no arquivo runtime.txt.

No aplicativo segue as configurações para acessar o banco de dados do Firebase na minha conta, para utilizar um novo banco de dados, crie a sua conta no Firebase e
coloque as suas credenciais no código no formato em que está nos arquivos 'views.py' nas pastas 'api' e 'exemplo'.
Para utilizar o Storage na sua conta, você deve baixar uma nova chave no site do firebase em Configurações > Contas de serviço > Gerar nova chave privada.

Obs: Se for disponibilizar o aplicativo para o público, lembre de esconder a secret key em settings.py, no site do Django tem instruções de como proceder.

Mais informações em comentários no código.