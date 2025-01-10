import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text
import os
import hashlib
import base64

# Conectar ao banco de dados MySQL
print("Conectando ao banco de dados...\n")

DATABASE = 'mysql+pymysql://root:1234@127.0.0.1:3306/senhas_db'

print("Conectado com sucesso!!!!\n")


# Definindo a base de dados
Base = declarative_base()

# Definindo a classe do model
class Senhas(Base):
    __tablename__ = 'senhas_db'
    ID = Column(Integer, autoincrement=True, primary_key=True)
    NOME = Column(String(20))
    SENHA = Column(Text)
    SALT = Column(Text)

# Criando o engine de conexão
engine = sqlalchemy.create_engine(DATABASE)

# Criando a tabela no banco de dados, se não existir
Base.metadata.create_all(engine)
    
# Criando a sessão para interagir com o banco
Session = sessionmaker(bind=engine)
session = Session()

# Função de aperta pra continuar KK
def press():
    press = input("Aperte qualquer tecla para seguir...")
# Função para gerar o salt
def gerar_salt(tamanho=16):
    return os.urandom(tamanho)  # Gera um salt aleatório de 16 bytes

# Função para gerar o hash da senha com o salt
def gerar_hash_com_salt(senha, salt):
    # Combina a senha com o salt
    senha_combinada = senha.encode('utf-8') + salt
    # Cria o hash usando SHA-256
    return hashlib.sha256(senha_combinada).hexdigest()

# Função para salvar a senha no banco de dados
def salvar_senha_no_banco(usuario, senha):
    # Gerar um salt único
    salt = gerar_salt()
    
    # Gerar o hash da senha com o salt
    hash_senha = gerar_hash_com_salt(senha, salt)

    # Inserir o usuário e a senha no banco de dados
    novo_usuario = Senhas(NOME=usuario, SENHA=hash_senha, SALT=base64.b64encode(salt).decode('utf-8'))
    session.add(novo_usuario)
    session.commit()
    print(f"Senha para o usuário '{usuario}' cadastrada com sucesso!")
    
    # verifica se ta sendo adicionado corretamente
    result = session.query(Senhas).filter_by(NOME=usuario, SENHA=hash_senha, SALT=base64.b64encode(salt).decode('utf-8')).first()
    # mostra os dados
    print(f"ID: {result.ID}\nNome: {result.NOME}\nSenha: {result.SENHA}\nSalt: {result.SALT}")
    print("-" * 20)
    press()

def select():
    # Buscar as senhas do banco de dados
    Buscar = input("Digite qual o usuario que dejesa ver a senha: ")
    senhas = session.query(Senhas).filter_by(NOME=Buscar).all()

    # Exibir as senhas
    for senha in senhas:
        print(f"Nome de usuário: {senha.NOME}")
        print(f"Senha: {senha.SENHA}")
        print(f"Salt: {senha.SALT}")
        print("-" * 20)
    
    press()

# Função para inserir uma senha interativamente
def insert():
    usuario = input("Digite o nome de usuário: ")
    senha = input("Digite a senha que deseja salvar: ")
    salvar_senha_no_banco(usuario, senha)

def update():
    update = input("Deseja atualizar a senha ou o usuario? \n")
    if update == "usuario":
        # Atualizar usuarios
        usuario_atual = input("Digite o nome de usuário que dejesa alterar: \n")
        result = session.query(Senhas).filter_by(NOME=usuario_atual).first()
        if result:
            print("Usuário encontrado com sucesso!")
            usuario_alterado = input("Digite qual o nome que dejesa colocar como usuario: \n")
            confimar = input(f"Tem certeza que deseja alterar{usuario_atual} para {usuario_alterado}? \n")
            if confimar == "sim":
                result.NOME = usuario_alterado
                session.commit()
                print("Usuário alterado com sucesso!")
                press()
            else:
                print("Usuário nao alterado!")
                press()
                escolher_opcao()
        else:
            print("Usuário nao encontrado!")
            press()
            escolher_opcao()
    elif update == "senha":
        # Atualizar senha
        usuario_atual = input("Digite o nome de usuário que dejesa alterar a senha: \n")
        result = session.query(Senhas).filter_by(NOME=usuario_atual).first()
        if result:
            print("Usuário encontrado com sucesso!")
            senha_alterada = input("Digite qual a senha que dejesa colocar: \n")
            confimar = input(f"Tem certeza que deseja alterar a senha de {usuario_atual}? \n")
            if confimar == "sim":
                salt = gerar_salt()
                hash_senha = gerar_hash_com_salt(senha_alterada, salt)
                result.SENHA = hash_senha
                result.SALT = base64.b64encode(salt).decode('utf-8')
                session.commit()
                print("Senha alterada com sucesso!")
                press()
            else:
                print("Senha nao alterada!")
                press()
                escolher_opcao()
        else:
            print("Usuário nao encontrado!")
            press()
            escolher_opcao()

def descriptografar():
    # Solicita o nome de usuário para buscar a senha
    usuario = input("Digite o nome de usuário que deseja ver a senha: ")
    
    # Busca as senha pelo nome do usuario
    senhas_armazenadas = session.query(Senhas).filter_by(NOME=usuario).all()
    
    # Verifica se o usuário existe
    if not senhas_armazenadas:
        print(f"Usuário {usuario} não encontrado!")
        return
    # Exibe as senhas armazenadas (hash e salt) no banco
    for usuario in senhas_armazenadas:
        print(f"Usuário: {usuario.NOME}")
        print(f"Senha armazenada (hash): {usuario.SENHA}")
        print(f"Salt armazenado: {usuario.SALT}")
        print("-" * 20)
        
        # Decodifica o salt armazenado
        salt_armazenado = base64.b64decode(usuario.SALT)
        
        # Solicita a senha ao usuário para verificação
        senha_fornecida = input(f"Digite a senha para o usuário {usuario.NOME}: ")

        # Gera o hash da senha fornecida pelo usuário combinada com o salt armazenado
        hash_senha_fornecida = gerar_hash_com_salt(senha_fornecida, salt_armazenado)
        
        # Compara o hash gerado com o hash armazenado no banco de dados
        if hash_senha_fornecida == usuario.SENHA:
            print(f"Senha correta! {senha_fornecida}")
            press()
        else:
            print("Senha incorreta!\n")

def deletar_senha():
    usuario = input("Digite o nome de usuário para deletar a senha: ")
    usuario_encontrado = session.query(Senhas).filter_by(NOME=usuario).first()
    if not usuario_encontrado:
        print(f"Usuário {usuario} não encontrado!")
        return

    # Confirmar a exclusão
    confirmacao = input(f"Tem certeza que deseja deletar a senha e o usuário '{usuario}'?: ")
    
    if confirmacao.lower() == 'sim':
        # Deletar o usuário do banco de dados
        session.delete(usuario_encontrado)
        session.commit()
        print(f"A senha e o usuário '{usuario}' foi deletada com sucesso!")
    else:
        print("Deleção cancelada.")

def escolher_opcao():
    print("Escolha o que deseja fazer: ")
    
    while True:
        print("1. Inserir senha")
        print("2. Consultar senha")
        print("3. Alterar senha ou usuario")
        print("4. Verificar senha")
        print("5. Deletar senha")
        print("6. Sair")

        opcoes = input("Digite o número da opção desejada: ")

        if opcoes == "1":
            insert()
        elif opcoes == "2":
            select()
        elif opcoes == "3":
            update()
        elif opcoes == "4":
            descriptografar()
        elif opcoes == "5":
            deletar_senha()
        elif opcoes == "6":
            break

print("Bem-vindo ao meu gerenciador de senhas!\n")
escolher_opcao()