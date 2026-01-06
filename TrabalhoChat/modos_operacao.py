import os # para contexto de criptografia, o os.urandom é melhor que o random puro, documentação: https://cryptography.io/en/stable/random-numbers/

# ----> usei a biblioteca cryptography.hazmat para ajudar em tudo que não é objetivo direto do trabalho
# documentação de todos os hazardous materials: https://cryptography.io/en/latest/hazmat/primitives/

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# documentação das primitivas de crip simetrica: https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.Cipher
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
# documentação das primitivas de crip assimetrica: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/
from cryptography.hazmat.primitives import hashes, serialization
# documentação para a chave de sessão e serialização: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/#cryptography.hazmat.primitives.serialization.PrivateFormat.encryption_builder

BLOCK_SIZE = 16 # tamanho de bloco do aes

# -> funções de padding
def padding(data):
    if isinstance(data, str): # verifica se recebeu uma string e converte para bytes
        data = data.encode('utf-8')
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE) # pega o resto da divisao por 16 e diminui do bloco
    padding = bytes([pad_len] * pad_len) # cria a sequencia de preenchimento
    return data + padding

def unpadding(padded_data):
    pad_len = padded_data[-1] # le apenas o último byte para descarte
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Padding deu errado, verifique se está usando o mesmo modo de operação")
    return padded_data[:-pad_len]

# -> funções do RSA 
def gerar_chave_rsa():
    private_key = rsa.generate_private_key(
        public_exponent=65537, # documentação recomenda usar esse número padrao
        key_size=2048 # podia ser 4096 tambem, 1024 é quebravel facilmente
    )
    public_key = private_key.public_key() # extrai a chave publica com a privada
    return private_key, public_key # retorna as duas

def encripta_chave_sessao(public_key, session_key):
    return public_key.encrypt( # chama o metodo de encriptação
        session_key, # dado que queremos esconder 
        asym_padding.OAEP( # adiciona um ruido aleatorio para aumentar a segurança
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decripta_chave_sessao(private_key, encrypted_session_key):
    return private_key.decrypt( # chama o metodo de desencriptação
        encrypted_session_key, # dados recebidos
        asym_padding.OAEP( # garante que seja a mesma aleatoriedade da encriptação
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# -> funções de serialização
def serializa_chave_publica(public_key):
    return public_key.public_bytes( # converte a chave em bytes
        encoding=serialization.Encoding.PEM, # usa o padrão PEM
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def carrega_chave_publica(pem_data):
    return serialization.load_pem_public_key( # le o formato pem feito na serialização
        pem_data
    )

class AES_Trabalho:
    def __init__(self, key):
        self.key = key # salva a chave de sessão do handshake
        self.cipher = Cipher(algorithms.AES(key), modes.ECB()) # aqui usamos o ECB para usar como base e fazer as operações do CBC e o CTR em cima disso

    def encripta_bloco_unico(self, block): # função auxiliar para encriptar um bloco
        encryptor = self.cipher.encryptor()
        return encryptor.update(block) + encryptor.finalize()

    def decripta_bloco_unico(self, block): # função auxiliar para desencriptar um bloco
        decryptor = self.cipher.decryptor()
        return decryptor.update(block) + decryptor.finalize()

    def xor_bytes(self, b1, b2): # função auxiliar para fazer um xor
        return bytes(x ^ y for x, y in zip(b1, b2)) # pega os bits da mesma posição em b1 e b2, faz o xor e converte para bytes

    def encripta_cbc(self, plaintext):
        padded_text = padding(plaintext) 
        iv = os.urandom(BLOCK_SIZE) # gera um iv de 16 bytes totalmente aleatorios
        encrypted_msg = b""
        previous_block = iv # variavel que vai ser responsavel pelo encadeamento do cbc, primeiro valor dela é o iv, depois disso vai ser resultado do bloco anterior
        for i in range(0, len(padded_text), BLOCK_SIZE): # loop pelos blocos
            current_block = padded_text[i : i + BLOCK_SIZE] # vai cortando intervalos de 16 bytes
            xor_result = self.xor_bytes(current_block, previous_block) # xor do atual com o anterior
            cipher_block = self.encripta_bloco_unico(xor_result) # faz a encriptação
            encrypted_msg += cipher_block
            previous_block = cipher_block
        return iv + encrypted_msg # retorna a mensagem e o iv

    def decripta_cbc(self, ciphertext_with_iv):
        iv = ciphertext_with_iv[:BLOCK_SIZE] # separa o iv do resto
        ciphertext = ciphertext_with_iv[BLOCK_SIZE:]
        decrypted_padded_msg = b""
        previous_block = iv

        for i in range(0, len(ciphertext), BLOCK_SIZE): # loop pelos blocos cifrados
            current_cipher_block = ciphertext[i : i + BLOCK_SIZE]
            decrypted_block_raw = self.decripta_bloco_unico(current_cipher_block) # decripta usando a chave atual
            plaintext_block = self.xor_bytes(decrypted_block_raw, previous_block) # e faz xor com o bloco anterior
            decrypted_padded_msg += plaintext_block
            previous_block = current_cipher_block
        try:
            return unpadding(decrypted_padded_msg) # retorna a mensagem sem o padding
        except Exception:
            return b"Erro no padding ou chave, verificar"

    def encripta_ctr(self, plaintext):
        nonce = os.urandom(8) # criamos o nounce com a metade do bloco, novamente totalmente aleatorio
        keystream = b""
        num_blocks = (len(plaintext) // BLOCK_SIZE) + 1 # calcula quantos blocos vão precisar para a mensagem inteira
        for counter in range(num_blocks):
            counter_bytes = counter.to_bytes(8, byteorder='big') # cria o counter com os 8 bytes, big é só para dizer que ele será tranformado em big endian
            input_block = nonce + counter_bytes # agrupa o nonce com o contador
            keystream_block = self.encripta_bloco_unico(input_block) # cifra o bloco e gera o bloco da keystream
            keystream += keystream_block
        keystream = keystream[:len(plaintext)]
        ciphertext = self.xor_bytes(plaintext, keystream) # xor da keystream com o texto plano
        return nonce + ciphertext

    def decripta_ctr(self, ciphertext_with_nonce):
        nonce = ciphertext_with_nonce[:8] # recupera o nonce e separa do texto cifrado
        ciphertext = ciphertext_with_nonce[8:]
        keystream = b""
        num_blocks = (len(ciphertext) // BLOCK_SIZE) + 1
        for counter in range(num_blocks): # recriamos o mesmo keystream
            counter_bytes = counter.to_bytes(8, byteorder='big')
            input_block = nonce + counter_bytes
            keystream_block = self.encripta_bloco_unico(input_block)
            keystream += keystream_block
        keystream = keystream[:len(ciphertext)]
        plaintext = self.xor_bytes(ciphertext, keystream) # fazemos xor, para recuperar agora o texto original
        return plaintext



