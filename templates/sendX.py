import socket
from threading import Thread
import json
import os

try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("Le fichier config.json est introuvable.")
    input("Appuyez sur ENTRER pour quitter.")
    exit(1)
# Constantes
IP = socket.gethostbyname(socket.gethostname())
HOSTNAME = config["HOSTNAME"] if config["HOSTNAME"] != "AUTO" else IP
PORT = config["PORT"]
BUFFER_SIZE = config["BUFFER_SIZE"]
SERVER_NAME = config["SERVER_NAME"]
WELCOME_MESSAGE = config["WELCOME_MESSAGE"]
MAX_CLIENTS = config["MAX_CONNECTIONS"]

# Listes globales
clients = []  # [(socket, name)]
message_queue = []  # [(message, sender)]
os.makedirs(os.path.join(os.path.dirname(__file__), "temp"), exist_ok=True)
tempFile = [f for f in os.listdir("temp") if os.path.isfile(os.path.join("temp", f))]

class commandes():
    """Classe pour gérer les commandes spéciales."""

    def __init__(self, requestBin, client):
        self.commands = {
            "!info": self.get_info,
            "!file_send": self.receive_file,
            "!file_list": self.send_file_liste,
            "!ask_file": self.send_file,
        }
        self.request = requestBin.decode("utf-8")
        self.requestBinary = requestBin
        self.client = client

    def get_info(self):
        """Retourne la liste des clients connectés."""
        self.connected_clients = get_connected_clients()
        return f"!info:{','.join(self.connected_clients)};{SERVER_NAME};{IP};{PORT}".encode("utf-8")
    
    def get_commands(self):
        """Retourne le dictionnaire des commandes."""
        return self.commands

    def receive_file(self):
        """Gère la réception de fichiers."""
        print("Réception de fichier...")
        trans_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        trans_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Fix: Allow port reuse
        trans_socket.bind((HOSTNAME, PORT + 1))
        trans_socket.listen(1)
        trans_client, addr = trans_socket.accept()
        
        # Recevoir la taille du nom du fichier
        fileNameSize = int.from_bytes(trans_client.recv(4), 'big')
        filename = trans_client.recv(fileNameSize).decode("utf-8")  # Recevoir le nom du fichier
        print(f"filename : {filename}")
        tempFile.append(filename)
        
        # Recevoir le contenu du fichier
        content = b""
        while True:
            chunk = trans_client.recv(BUFFER_SIZE)
            if not chunk:
                break
            content += chunk
        
        with open(os.path.join("temp", filename), "wb") as f:
            f.write(content)  # Écrire le contenu du fichier
        print(f"Fichier reçu : {filename}")
        broadcast(f"Fichier disponible : {filename};serveur", exclude_client=self.client)
        self.client.send(f"OK; serveur".encode("utf-8"))
        trans_client.close()
        trans_socket.close()
        return None

    def send_file_liste(self):
        """Retourne la liste des fichiers disponibles."""
        if len(tempFile) == 0:
            self.client.send(f"!availble:NO".encode("utf-8"))
            return None
        else:
            files = ";".join(tempFile)
            self.client.send(f"!availble:{files}".encode("utf-8"))
            return None

    def send_file(self):
        """Envoie un fichier à un client."""
        trans_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        trans_socket.bind((HOSTNAME, PORT + 1))
        trans_socket.listen(1)
        print("En attente de connexion pour l'envoi de fichier...")
        trans_client, addr = trans_socket.accept()

        file_name = trans_client.recv(1024).decode("utf-8")  # Recevoir la demande de fichier
        if file_name in tempFile:
            trans_client.send("OK".encode("utf-8"))
            file_path = os.path.join("temp", file_name)
            with open(file_path, "rb") as f:
                content = f.read()
            trans_client.send(content)
        else:
            trans_client.send("NO".encode("utf-8"))
def encode_list(lst):
    """Encode une liste en chaîne UTF-8 séparée par des ';'."""
    return ";".join(lst).encode("utf-8")

def decode_list(encoded_lst):
    """Décode une chaîne UTF-8 en liste."""
    return encoded_lst.decode("utf-8").split(";")

def broadcast(message, exclude_client=None):
    """Envoie un message à tous les clients sauf celui spécifié."""
    for client, _ in clients:
        if client != exclude_client:
            try:
                client.send(message.encode("utf-8"))
            except Exception as e:
                print(f"Erreur lors de l'envoi à un client : {e}")

def get_connected_clients():
    """Retourne une liste des noms des clients connectés."""
    lst = [name for _, name in clients]
    return lst

def find_client_by_name(name):
    """Trouve un socket client par son nom."""
    for client, client_name in clients:
        if client_name == name:
            return client
    return None

def handle_client(client, name):
    """Gère la communication avec un client."""
    while True:
        try:
            request = client.recv(BUFFER_SIZE)
            requestBinary = request
            request = request.decode("utf-8")
            if not request:
                raise ConnectionResetError
            
            else:
                if request.startswith("!"):
                    cmdInstance = commandes(requestBinary, client)
                    cmd = cmdInstance.get_commands()
                    commande = request.split(":")[0]
                    print(f"commande:{commande}")
                    if commande in cmd:
                        print("commande ok")
                        result = cmd[commande]()
                        if result is not None:
                            client.send(result)
                    else:
                        client.send("!unknown".encode("utf-8"))
                else:
                    message_queue.append((request, name))
        except Exception as e:
            print(f"Déconnexion de {name} : {e}")
            clients.remove((client, name))
            broadcast(f"{name} a quitté la discussion !;serveur")
            break

def process_messages():
    """Thread pour traiter les messages en file d'attente."""
    while True:
        if message_queue:
            message, sender = message_queue.pop(0)
            formatted_message = f"{message};{sender}"
            broadcast(formatted_message)

def handle_new_connection(client):
    """Gère une nouvelle connexion client."""
    if len(clients) >= MAX_CLIENTS:
        client.send("FULL".encode("utf-8"))
        client.close()
        return None
    else:
        try:
            client.send("OK".encode("utf-8"))
            name = client.recv(BUFFER_SIZE).decode("utf-8")
            if any(name == client_name for _, client_name in clients):
                client.send("NO".encode("utf-8"))
                client.close()
                return None
            clients.append((client, name))
            client.send("OK".encode("utf-8"))
            client.send(encode_list(get_connected_clients()))
            client.send(f"{SERVER_NAME};{WELCOME_MESSAGE}".encode("utf-8"))
            broadcast(f"{name} a rejoint la discussion !;serveur", exclude_client=client)
            return name
        except Exception as e:
            print(f"Erreur lors de la connexion d'un client : {e}")
            client.close()
            return None
