import socket
from threading import Thread
import os
import sys

# Constantes
SERVEUR_HOSTNAME = input("ip du serveur >>>")  # IP du serveur

PORT = 8888  # Port du serveur

class Commandes:
    def __init__(self, serv_socket):
        """Initialise la classe avec une socket serveur."""
        self.serv_socket = serv_socket

        # Dictionnaire des commandes après la définition des méthodes
        self.liste = {
            "!quit": self.bye,
            "!hello": self.hello,
            "!getInfo": self.get_info,
            "!help": self._help,
            "!clear": self.clear,
            "!file": self._file,
            "!file_liste": self.file_liste,
            "!get_file": self.get_file,
        }

    commandes_help = [
        "!quit: quitter la discussion",
        "!hello: dire bonjour",
        "!getInfo: obtenir la liste des informations",
        "!help: afficher les commandes disponibles",
        "!clear: effacer l'écran",
        "!file: envoyer un fichier (en cours de développement)",
    ]

    def _help(self):
        """Afficher les commandes disponibles."""
        print("Voici les commandes disponibles :")
        for cmd in self.commandes_help:
            print(f"    {cmd}")
        print("Entrez une commande pour l'exécuter.")

    def clear(self):
        """Effacer l'écran."""
        os.system("cls" if os.name == "nt" else "clear")

    def bye(self):
        """Envoyer un message de déconnexion au serveur et fermer la connexion."""
        self.serv_socket.send("!quit".encode("utf-8"))
        self.serv_socket.close()

    def hello(self):
        """Envoyer un message de salutation au serveur."""
        self.serv_socket.send("Salut tout le monde !".encode("utf-8"))

    def get_info(self):
        """Envoyer une demande d'informations au serveur."""
        self.serv_socket.send("!info".encode("utf-8"))

    def _file(self):
        """Envoyer un fichier au serveur (fonctionnalité en cours de développement)."""
        path = input("Quel est le nom du fichier ? >>> ")
        fileName = os.path.basename(path)
        if not os.path.isfile(path):
            print("Le fichier n'existe pas.")
            return
        file = f"!file_send:{fileName};".encode("utf-8")
        try:
            with open(path, "rb") as f:
                file += f.read()
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier : {e}")
            return
        self.serv_socket.send(file)
    def file_liste(self):
        """Envoyer une liste de fichiers au serveur."""
        self.serv_socket.send("!file_liste".encode("utf-8"))
    def get_file(self):
        """Envoyer une demande de fichier au serveur."""
        fileName = input("Quel est le nom du fichier ? >>> ")
        self.serv_socket.send(f"!ask_file:{fileName}".encode("utf-8"))
def decodeLst(encodedLst):
    """Décoder une liste encodée en UTF-8."""
    return encodedLst.decode("utf-8").split(";")


def send(serv_socket, commandes):
    """Thread pour envoyer des messages au serveur."""
    while True:
        try:
            def clear_input_line():
                """Efface la ligne actuelle dans la console."""
                sys.stdout.write("\033[K")
                sys.stdout.flush()

            def move_cursor_to_bottom():
                """Déplace le curseur en bas de l'écran."""
                rows, _ = os.get_terminal_size()
                sys.stdout.write(f"\033[{rows};0H")
                sys.stdout.flush()

            while True:
                move_cursor_to_bottom()
                clear_input_line()
                brutInput = input("")
                if brutInput.startswith("!"):
                    if brutInput in commandes.liste:
                        try:
                            commandes.liste[brutInput]()
                        except Exception as e:
                            print(f"Erreur lors de l'exécution de la commande : {e}")
                    else:
                        serv_socket.send(brutInput.encode("utf-8"))
                else:
                    if ";" in brutInput:
                        print("Le caractère ';' n'est pas accepté.")
                    else:
                        serv_socket.send(brutInput.encode("utf-8"))
        except Exception as e:
            print(f"Erreur lors de l'envoi : {e}")
            break

def receive(serv_socket, name):
    """Thread pour recevoir des messages du serveur."""
    while True:
        try:
            message = serv_socket.recv(1024).decode("utf-8")
            if message.startswith("!"):
                if message != "!unknown":
                    command, *data = message.split(":")
                    data = data[0].split(";")
                    if command == "!info":
                        namesC = data[0].split(",")
                        servName = data[1]
                        ip = data[2]
                        port = data[3]
                        print("Voici les informations du serveur :")
                        print(f"Serveur : {servName} ({ip}:{port})")
                        print("Voici les personnes connectées :")
                        for user in namesC:
                            print(f"    {user}")
                    if command == "!availble":
                        if data[0] == "NO":
                            print("aucun fichier disponible")
                        else:
                            print("Voici les fichiers disponibles :")
                            for i in data:
                                print(f"    {i}")
                    if command == "!file_send":
                        fileName = data[0]
                        file = data[1].encode("utf-8")
                        os.makedirs(os.path.join(os.path.dirname(__file__), "received"), exist_ok=True)
                        path = os.path.join(os.path.dirname(__file__), "received", fileName)
                        with open(path, "xb") as f:
                            f.write(file)
                        print(f"Fichier {fileName} reçu.")
                else:
                    print("Commande inconnue.")
            else:
                contenu, sender = message.split(";")
                if sender != name.decode("utf-8"):
                    print(f"{sender}: {contenu}")
        except Exception as e:
            print(f"Déconnexion : {e}")
            break

# Connexion au serveur
nameBrut = input("Quel est votre nom ? >>> ")
name = nameBrut.encode("utf-8")
try:
    servSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servSocket.connect((SERVEUR_HOSTNAME, PORT))
except Exception as e:
    print(f"Serveur indisponible : {e}")
    print("L'ip est peut-être incorrecte")
    input("Appuyez sur ENTRER pour quitter.")
    exit()

# Authentification
first = servSocket.recv(1024)
if first.decode("utf-8") != "OK":
    print("Le serveur est plein.")
    input("Appuyez sur ENTRER pour quitter.")
    exit(1)
servSocket.send(name)
retour = servSocket.recv(1024).decode("utf-8")
if retour == "OK":
    pass
elif retour == "NO":
    print("Nom déjà pris...")
    input("Appuyez sur ENTRER pour quitter.")
    exit(2)
else:
    print("Un problème est survenu.")
    input("Appuyez sur ENTRER pour quitter.")
    exit(1)

# Affichage des utilisateurs connectés
names = decodeLst(servSocket.recv(1024))
servName, welcomeMessage = servSocket.recv(1024).decode("utf-8").split(";")
print(f"Serveur : {servName}")
print(f"{welcomeMessage}")
print("Voici les personnes connectées :")
for i, nameDisplay in enumerate(names, start=1):
    info = "(vous)" if nameDisplay == nameBrut else ""
    print(f"{i}. {nameDisplay} {info}")

# Initialisation des commandes
commandes = Commandes(servSocket)

# Lancement des threads
recpt = Thread(target=receive, args=(servSocket, name), daemon=True)
sending = Thread(target=send, args=(servSocket, commandes), daemon=True)

recpt.start()
sending.start()

sending.join()
