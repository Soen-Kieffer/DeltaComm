import socket
from threading import Thread
import json

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

class commandes():
    """Classe pour gérer les commandes spéciales."""

    def __init__(self):
        self.commands = {
            "!info": self.get_info,
        }

    def get_info(self):
        """Retourne la liste des clients connectés."""
        self.connected_clients = get_connected_clients()
        return f"!info:{','.join(self.connected_clients)};{SERVER_NAME};{IP};{PORT}".encode("utf-8")
    
    def get_commands(self):
        """Retourne le dictionnaire des commandes."""
        return self.commands

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
    print(lst)
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
            request = client.recv(BUFFER_SIZE).decode("utf-8")
            if not request:
                raise ConnectionResetError
            
            else:
                if request.startswith("!"):
                    cmdInstance = commandes()
                    cmd = cmdInstance.get_commands()
                    if request in cmd:
                        request = cmd[request]()
                        if type(request) == bytes:
                            client.send(request)
                        else:
                            client.send(request.encode("utf-8"))
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
