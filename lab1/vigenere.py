# Talvez seja necessário mudar o parâmetro do método "with open" do testes.txt para usar, usei o 
# caminho relativo do meu arquivo('../Criptografia/lab1/testes.txt'), então vou colocar um aviso
# na parte que talvez seja necessário realizar a mudança.

def encriptar(texto_claro, chave): # aqui vamos encriptar usando um texto claro e uma cifra, que podem ser alterados no arquivo "testes.txt"
    if not texto_claro:
        return ("Não foi possível realizar a encriptação. O TEXTO CLARO é vazio")
    if not chave:
        return ("Não foi possível realizar a encriptação. A CHAVE é vazia")
    
    texto_encriptado = ''
    tamanho_chave = len(chave)

    for i in range(len(texto_claro)):
        valor_letra = ord(texto_claro[i]) # deus abençoe o invetor da função ord
        valor_chave = ord(chave[i % tamanho_chave]) # usando para a chave voltar ao começo quanddo acabar
        valor_encriptado = (valor_letra + valor_chave) % 256 # matematica para descobrir o número na tabela acii padrão ou ascii estendida que a letra vai representar
        texto_encriptado += chr(valor_encriptado) # deus abençoe o inventou da função chr
    return texto_encriptado


def desencriptar(texto_encriptado, chave):
    if not texto_encriptado:
        return ("Não foi possível realizar a desencriptação. O TEXTO ENCRIPTADO é vazio")
    if not chave:
        return ("Não foi possível realizar a desencriptação. A CHAVE é vazia")
    
    texto_claro = ''
    tamanho_chave = len(chave)

    for i in range(len(texto_encriptado)):
        valor_letra = ord(texto_encriptado[i])
        valor_chave = ord(chave[i % tamanho_chave])
        valor_desencriptado = (valor_letra - valor_chave + 256) % 256 # matematica para reverter a encriptação
        texto_claro += chr(valor_desencriptado)
    return texto_claro


def converte_decimal(texto):
    # alguns caracteres da tabela ascii completa não podem ser impressos
    # os 32 primeiros de controle e a ascii extendida,
    # então essa parte é pra fazer algo com esses resultaddos
    if not texto:
        return ("Não foi possível realizar a conversão. O TEXTO é vazio")
    lista = []
    
    for caractere in texto: # percorrendo tds os caracteres do texto e faz operações de transformar em decimal -> string -> add a string na lista
        valor_decimal = ord(caractere)
        string_decimal = str(valor_decimal)
        lista.append(string_decimal) 
    texto_final = ' '.join(lista) # junta tudo e separa com um espaço, então agora os caracteres "invisiveis" tem pelo menos um valor para consulta
    return texto_final


def ler_teste():
    print("----- BEM-VINDO À CIFRA DE VIGENERE.PY -----")
    try:
        with open('../Criptografia/lab1/testes.txt', 'r', encoding='utf-8') as testes: # AVISO!!! SE NECESSÁRIO, MUDE O CAMINHO DO ARQUIVO
            for i, linha in enumerate(testes):
                if i == 0: continue # pulando o cabeçalho (linha 0)
                partes = linha.strip().split(';')
                if len(partes) == 3: # garantia q cada linha tem 3 partes
                    descricao, texto_claro, chave = partes
                    print(f"\n--- Teste : {descricao} ---") # descricao do teste
                    print(f"Texto Claro : '{texto_claro}'") # texto claro do teste
                    print(f"Chave : '{chave}'") # chave do teste

                    texto_encriptado = encriptar(texto_claro, chave) # passando o texto_claro e a chave para a função de encriptar e guadando na variavel
                    texto_desencriptado = desencriptar(texto_encriptado, chave) # passando o texto_encriptaddo e a chave para a função de desencriptar e guadando na variavel
                    print(f"Texto Encriptado : '{texto_encriptado}'") # print do texto (tentativa)
                    print(f"Representação Decimal : '{converte_decimal(texto_encriptado)}'") # print da representação decimal de cada caracter(se o encriptado não imprimir)
                    print(f"Texto Desencriptado : '{texto_desencriptado}'") # texto depois de ser desencriptado

                    if texto_claro == texto_desencriptado: # prova final para testar se funcionou
                        print("Resultado : SUCESSO")
                    else:
                        print("Resultado : FALHA")
    except FileNotFoundError:
        print("\nArquivo 'testes.txt' não encontrado, tente mudar o caminho!!")


if __name__ == "__main__":
    ler_teste()