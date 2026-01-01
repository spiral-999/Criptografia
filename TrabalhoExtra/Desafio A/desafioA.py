# Desafio A: Quebrando a Resistência a Colisões. A resistência a colisões afirma que deve ser
# difícil encontrar dois valores x e y quaisquer, tal que H(x) = H(y).

# Tarefa: Escreva um programa que encontre duas strings diferentes que gerem exatamente o
# mesmo hash de 4 bytes.

import hashlib
import string
import random
import csv

BYTES_SAIDA = 4 
ARQUIVO_DB = r".\TrabalhoExtra\Desafio A\hashes_desafioA.csv" # mude o caminho aqui se precisar

def gerar_string_aleatoria(): # gera uma string aleatoria de 1 a 6 caracteres, sendo formada por letras e numeros
    caracteres = string.ascii_letters + string.digits
    tamanho = random.randint(1, 6)
    return ''.join(random.choices(caracteres, k=tamanho))

def main():
    print("Desafio A: Quebrando a Resistência a Colisões")
    print("---------------------------------------------")

    with open(ARQUIVO_DB, mode='w', newline='') as file: # cria o arquivo csv que vai guardar as tentativas
        writer = csv.writer(file)
        writer.writerow(["Hash", "String"])
    
    print(f"Arquivo CSV criado em {ARQUIVO_DB}, abra e verifique o progresso")

    hashes_vistos = set()
    tentativas = 0
    
    # LOOP INFINITO
    while True:
        string_nova = gerar_string_aleatoria()
        hash_novo = hashlib.shake_128(string_nova.encode('utf-8')).hexdigest(BYTES_SAIDA) # calcula o hash com SHAKE128 e pega 4 bytes
        if hash_novo in hashes_vistos: # se o hash é repetido, vamos verificar no csv
            with open(ARQUIVO_DB, mode='r') as file:
                reader = csv.reader(file)
                next(reader)
                for linha in reader:
                    hash_antigo = linha[0]
                    string_antiga = linha[1]
                    if hash_antigo == hash_novo: # se encontramos o mesmo hash
                        if string_antiga != string_nova: # se a string é diferente, assim garantimos a veradeira colisao
                            with open(ARQUIVO_DB, mode='a', newline='') as f_out:
                                w = csv.writer(f_out)
                                w.writerow([hash_novo, string_nova])
                            print("-----------------------")
                            print(f"\n COLISÃO ENCONTRADA")
                            print(f"Hash de Ambos : {hash_novo}")
                            print(f"String 1 : '{string_antiga}'")
                            print(f"String 2 : '{string_nova}'")
                            return
                        else: # mesmo hash e strings iguais não é colisao
                            break 
        else: # se o hash é novo salvamos na memoria e no arquivo csv
            hashes_vistos.add(hash_novo)
            with open(ARQUIVO_DB, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([hash_novo, string_nova])

        tentativas += 1
        if tentativas % 1000 == 0:
            print(f"Tentativas : {tentativas}")

if __name__ == "__main__":
    main()