# Desafio B: Quebrando a Segunda Pré-imagem. Dado uma entrada x1, deve ser difícil encontrar
# um x2 ̸= x1 tal que H(x1) = H(x2).

# Considere a seguinte entrada fixa no sistema:
# Entrada Alvo (x1): "Aluno: <Seu Nome Completo>"

# Configuração: Tamanho de saída de 4 bytes.

# Tarefa: Encontre qualquer outra string (x2) que gere o mesmo hash que o seu nome.

import hashlib
import string
import random
import csv
import time

BYTES_SAIDA = 4 
NOME_ALUNO = "Mateus Lima Rodrigues"
ARQUIVO_LOG = r".\TrabalhoExtra\Desafio B\log_desafioB.csv"

def gerar_string_aleatoria(): # também gera uma string aleatoria, mas dessa vez bem maior tendo de 1 a 12 digitos
    caracteres = string.ascii_letters + string.digits
    tamanho = random.randint(1, 12) # aumentar o tamanho serve apenas para aumentar os "chutes"
    return ''.join(random.choices(caracteres, k=tamanho))

def main():
    print("Desafio B: Quebrando a Segunda Pré-imagem")
    print("------------------------------------------")
    
    input_alvo = f"Aluno: {NOME_ALUNO}"
    hash_alvo = hashlib.shake_128(input_alvo.encode('utf-8')).hexdigest(BYTES_SAIDA)
    
    print(f"Entrada Alvo(x1) : '{input_alvo}'") # entrada nome que definimos
    print(f"Hash do Alvo(H(x1)) : {hash_alvo}") # hash do nome definido
    print("-------------------------------------------------------------")

    # aqui o csv vai salvar apenas o progresso, tipo um checkpoint
    with open(ARQUIVO_LOG, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Horário", "Tentativas", "Status", "Ultima_String", "Ultimo_Hash"])
        writer.writerow(["---", "---", "META_DO_DESAFIO", f"ALVO : {input_alvo}", f"HASH : {hash_alvo}"])
    
    print(f"Arquivo CSV criado em {ARQUIVO_LOG}, abra e verifique o progresso")
    
    tentativas = 0
    inicio = time.time()
    
    while True: # loop infinito ate encontar
        string = gerar_string_aleatoria()

        if string == input_alvo: # nao pode permitir que seja a mesma string, mesmo que nunca va acontecer
            continue
            
        hash = hashlib.shake_128(string.encode('utf-8')).hexdigest(BYTES_SAIDA)
        
        if hash == hash_alvo: # achou o mesmo hash
            fim = time.time()
            tempo_total = fim - inicio
            print("---------------------------------")
            print(f"\n SEGUNDA PRÉ-IMAGEM ENCONTRADA")
            print(f"Entrada Alvo(x1) : '{input_alvo}'")
            print(f"Outra String(x2): '{string}'")
            print(f"Hash de Ambos : {hash_alvo}")
            print(f"Tempo Para Encontrar : {tempo_total:.2f} segundos")
            
            with open(ARQUIVO_LOG, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([time.ctime(), tentativas, "SUCESSO_FINAL", string, hash])
            return

        tentativas += 1
        if tentativas % 500000 == 0: # o checkpoint vai sendo salvo a cada 500000 tentativas
            print(f"Tentativas : {tentativas} / Última String : {string} / Hash da String : {hash}")
            print("---------------------------------------------------------------------------------")
            with open(ARQUIVO_LOG, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([time.ctime(), tentativas, "EM_ANDAMENTO", string, hash])

if __name__ == "__main__":
    main()