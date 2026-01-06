import socket # biblioteca p comunicação em rede
import threading # para fazer duas coisas ao mesmo tempo, esperar a mensagem e digitar
import os
import modos_operacao as ferramentas # arquivo dos modos de operação

HOST = '127.0.0.1' # localhost
PORT = 5555

def imprimir_log_seguranca(etapa, dados_originais, dados_cifrados, extra_info=""): # funcao para mostrar detalhes do log
    print("--------------------------------------")
    print(f"\n LOG DE SEGURANÇA DETALHADO : {etapa}")
    if dados_originais:
        print(f"Mensagem Original : {dados_originais}")
    if extra_info:
        print(f"Detalhes : {extra_info}")
    hex_cifrado = dados_cifrados.hex().upper()
    display_hex = hex_cifrado if len(hex_cifrado) < 60 else f"{hex_cifrado[:30]}...{hex_cifrado[-30:]}" # se ficar muito grande, mostra só o começo e o final
    print(f"Dados Trafegados : {display_hex}")
    print("--------------------------------------")

class ChatP2P:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria o socket
        self.aes = None # instanciado apos o handshake
        self.modo_op = 'CTR' # modo padrao
        
    def iniciar(self):
        print("CHAT SEGURO P2P - TRABALHO DE CRIPTOGRAFIA")
        print("1. Iniciar como SERVIDOR") # selecione e aguarde a conexão
        print("2. Iniciar como CLIENTE") # conecta com o servidor
        opcao = input("Escolha : ")

        # menu para escolher o modo de operação do AES
        print("\nAgora escolha o Modo de Operação")
        print("1. CTR (Counter)")
        print("2. CBC (Cypher Block Chaining)")
        modo = input("Escolha (1 para usar o CTR ou 2 para CBC) : ")
        self.modo_op = 'CBC' if modo == '2' else 'CTR'
        print(f"Modo selecionado: {self.modo_op}")
        if opcao == '1':
            self.servidor()
        else:
            self.cliente()

    def servidor(self):
        self.sock.bind((HOST, PORT))
        self.sock.listen(1) # permite uma conexão apenas, modelo P2P
        print(f"\nEsperando conexão na porta {PORT}") # escuta a porta e espera a conexão
        conn, addr = self.sock.accept() # trava quando encontra a conexão
        print(f"Conexão estabelecida com {addr}")
        
        print("\nGerando par de chaves RSA para o Handshake")
        priv_rsa, pub_rsa = ferramentas.gerar_chave_rsa() # chama a funcao para criar as chaves
        pub_pem = ferramentas.serializa_chave_publica(pub_rsa) # serializa as chaves(PEM)
        conn.send(pub_pem) # manda pra o cliente
        print("Chave Pública RSA enviada")
        
        encrypted_session_key = conn.recv(2048) # recebe a chave de sessão

        session_key = ferramentas.decripta_chave_sessao(priv_rsa, encrypted_session_key) # decripta a sessão usando a privada
        print(f"Chave de Sessão recebida e decriptada : {session_key.hex()}")
        
        self.aes = ferramentas.AES_Trabalho(session_key)
        self.loop_chat(conn)

    def cliente(self):
        print(f"\nTentando conectar em {HOST}:{PORT}")
        self.sock.connect((HOST, PORT)) # bate na porta do servidor que está esperando
        
        print("Aguardando Chave Pública do Servidor")
        pub_pem = self.sock.recv(2048) # le os bytes que chegaram
        pub_rsa = ferramentas.carrega_chave_publica(pub_pem) # envia para a funcao e reconstroi a chave
        print("Chave Pública RSA recebida")
        
        session_key = os.urandom(32) # gera a chave de sessão aleatoria com 32 bytes
        print(f"Chave de Sessão gerada : {session_key.hex()}")
        
        encrypted_session_key = ferramentas.encripta_chave_sessao(pub_rsa, session_key) # cifra a chave de sessão
        self.sock.send(encrypted_session_key) # envia para o servidor
        print("Chave de Sessão Enviada")

        self.aes = ferramentas.AES_Trabalho(session_key)
        self.loop_chat(self.sock)

    def loop_chat(self, connection):
        print("\n-------------------------------------")
        print(f"CHAT INICIADO - MODO {self.modo_op}")
        print("-------------------------------------\n")

        t_recv = threading.Thread(target=self.receber_msgs, args=(connection,)) # inicia thread para ficar escutando sem travar
        t_recv.start()

        while True:
            msg = input("Você : ")
            try:
                msg_bytes = msg.encode('utf-8') # transforma o texto em bytes
                ciphertext = b""
                if self.modo_op == 'CBC':
                    ciphertext = self.aes.encripta_cbc(msg_bytes) # envia para a encriptação do CBC
                    extra_info = f"IV={ciphertext[:16].hex()}" # pega o iv para mostrar no log

                else: # CTR
                    ciphertext = self.aes.encripta_ctr(msg_bytes) # envia para a encriptação do CTR
                    extra_info = f"Nonce={ciphertext[:8].hex()}" # pega o CTR para mostar no log

                imprimir_log_seguranca("ENVIANDO", msg, ciphertext, extra_info)
                connection.send(ciphertext) # dps de tudo envia os bytes cifrados para a rede
                
            except Exception as e:
                print(f"Falha ao enviar : {e}")
                break

    def receber_msgs(self, connection):
        while True:
            try:
                data = connection.recv(1024) # tamanho do buffer
                if not data:
                    print("\nO outro usuário desconectou")
                    break
                
                plaintext = b""
                
                if self.modo_op == 'CBC':
                    plaintext = self.aes.decripta_cbc(data) # manda p decriptação do CBC

                else: # CTR
                    plaintext = self.aes.decripta_ctr(data) # manda p decriptação do CTR

                msg_decoded = plaintext.decode('utf-8') # volta os bytes para string
                print(f"\n\nRecebido Criptografado : {data.hex().upper()}")
                print(f"-> AMIGO : {msg_decoded}")
                print("Você : ", end="", flush=True)
            except Exception as e:
                print(f"\nFalha ao receber : {e}")
                connection.close()
                break

if __name__ == "__main__":
    app = ChatP2P()
    app.iniciar()