import hashlib
import string
import random
import csv
import time

BYTES_SAIDA = 4 
HASH_ALVO_HEX = "AE27918D" # hash 4  que escolhi 
ARQUIVO_LOG = r".\TrabalhoExtra\Desafio C\log_desafioC.csv"

def gerar_string_aleatoria(): # mesma função aleatoria do desafio B
    caracteres = string.ascii_letters + string.digits
    tamanho = random.randint(1, 12)
    return ''.join(random.choices(caracteres, k=tamanho))

def main():
    print("Desafio C: Quebrando a Pré-imagem")
    print("----------------------------------")

    target_lower = HASH_ALVO_HEX.lower() # só para normalizar, o hashlib só usa letras minusculas

    print(f"Hash Alvo (Prefixo) : {HASH_ALVO_HEX}")
    print(f"Hash Procurado : {target_lower}")
    print("----------------------------------")

    with open(ARQUIVO_LOG, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Horario", "Tentativas", "Status", "Ultima_String", "Ultimo_Hash"]) 
        writer.writerow(["---", "---", "META", "RECUPERAR_SENHA", target_lower])
    
    tentativas = 0
    inicio = time.time()
    
    while True: # mesmo loop infinito de todos os exemplos
        string = gerar_string_aleatoria()
        hash = hashlib.shake_128(string.encode('utf-8')).hexdigest(BYTES_SAIDA)
        
        if hash == target_lower: # verificamos se o hash de agora é igual a senha que temos 
            fim = time.time()
            tempo_total = fim - inicio
            
            print("--------------------------")
            print(f"\n PRÉ-IMAGEM ENCONTRADA")
            print(f"Hash Alvo : {HASH_ALVO_HEX}")
            print(f"Hash da Última String : {hash}")
            print(f"Senha Descoberta : '{string}'")
            print(f"Tempo Decorrido : {tempo_total:.2f} segundos")
            
            with open(ARQUIVO_LOG, mode='a', newline='') as file: # salva o último no csv
                writer = csv.writer(file)
                writer.writerow([time.ctime(), tentativas, "SUCESSO_FINAL", string, hash, f"{tempo_total:.2f}s"])
            return

        tentativas += 1
        
        if tentativas % 500000 == 0: # mesmo checkpoint do exemplo anterior
            print(f"Tentativas : {tentativas} / Última String : {string} / Hash da String : {hash}")
            print("---------------------------------------------------------------------------------")
            with open(ARQUIVO_LOG, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([time.ctime(), tentativas, "EM_ANDAMENTO", string, hash])


if __name__ == "__main__":
    main()