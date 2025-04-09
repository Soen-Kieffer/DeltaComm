import socket
from threading import Thread
import os
import sys
import time

# Constantes
SERVEUR_HOSTNAME = "192.168.1.38"  # IP du serveur
PORT = 8888  # Port du serveur
BUFFER_SIZE = 1024

class Commandes:
    def __init__(self, serv_socket):
        """Initialise la classe avec une socket serveur."""
        self.serv_socket = serv_socket

        # Dictionnaire des commandes
        self.liste = {
            "!quit": self.bye,
            "!hello": self.hello,
            "!getInfo": self.get_info,
            "!help": self._help,
            "!clear": self.clear,
            "!file": self._file,
            "!file_list": self.file_liste,
            "!get_file": self.get_file,
        }

    commandes_help = [
        "!quit: quitter la discussion",
        "!hello: dire bonjour",
        "!getInfo: obtenir la liste des informations",
        "!help: afficher les commandes disponibles",
        "!clear: effacer l'écran",
        "!file: envoyer un fichier",
        "!file_list: lister les fichiers disponibles",
        "!get_file: télécharger un fichier",
    ]

    def _help(self):
        """Afficher les commandes disponibles."""
        print("Voici les commandes disponibles :")
        for cmd in self.commandes_help:
            print(f"    {cmd}")

    def clear(self):
        """Effacer l'écran."""
        os.system("cls" if os.name == "nt" else "clear")

    def bye(self):
        """Envoyer un message de déconnexion au serveur et fermer la connexion."""
        self.serv_socket.send("!quit".encode("utf-8"))
        self.serv_socket.close()

    def hello(self):
        """Envoyer un message de salutation au serveur."""
        self.serv_socket.send("Bonjour à tous !".encode("utf-8"))

    def get_info(self):
        """Envoyer une demande d'informations au serveur."""
        self.serv_socket.send("!info".encode("utf-8"))

    def _file(self):
        """Envoyer un fichier au serveur."""
        path = input("Quel est le nom du fichier ? >>> ")
        if not os.path.isfile(path):
            print("Le fichier n'existe pas.")
            return

        fileName = os.path.basename(path)
        try:
            self.serv_socket.send("!file_send".encode("utf-8"))

            # Ouvrir une connexion socket pour le transfert
            trans_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            trans_socket.connect((SERVEUR_HOSTNAME, PORT + 1))
            # Envoyer la taille du nom du fichier
            fileNameSize = len(fileName).to_bytes(4, 'big')
            trans_socket.send(fileNameSize)
            trans_socket.send(fileName.encode("utf-8"))

            # Envoyer le contenu du fichier
            with open(path, "rb") as f:
                while chunk := f.read(BUFFER_SIZE):
                    trans_socket.send(chunk)

            print(f"Fichier {fileName} envoyé avec succès.")
            trans_socket.close()
        except Exception as e:
            print(f"Erreur lors de l'envoi du fichier : {e}")

    def file_liste(self):
        """Envoyer une demande de liste de fichiers au serveur."""
        self.serv_socket.send("!file_list".encode("utf-8"))
    def get_file(self):
        fileName = input("Quel est le nom du fichier ? >>> ")
        self.serv_socket.send("!ask_file".encode("utf-8"))
        trans_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        trans_socket.connect((SERVEUR_HOSTNAME, PORT + 1))
        trans_socket.send(fileName.encode("utf-8"))
        reponse = trans_socket.recv(1024).decode("utf-8")
        if reponse == "OK":
            content = trans_socket.recv(1024)
            file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "received", fileName))
            dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"received"))
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except PermissionError:
                    print("Erreur : Impossible de créer le dossier 'received'. Vérifiez les permissions.")
                    return
            with open(file_path, "wb") as f:
                f.write(content)
            print(f"Fichier {fileName} téléchargé avec succès.")
        else:
            print("Le fichier n'est pas disponible.")
            trans_socket.close()
            return None


def decodeLst(encodedLst):
    """Décoder une liste encodée en UTF-8."""
    return encodedLst.decode("utf-8").split(";")

def send(serv_socket, commandes):
    """Thread pour envoyer des messages au serveur."""
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
        try:
            clear_input_line()
            move_cursor_to_bottom()
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
                            print("Aucun fichier disponible.")
                        else:
                            print("Voici les fichiers disponibles :")
                            for i in data:
                                print(f"    {i}")
                else:
                    print("Erreur : commande inconnue.")
            else:
                contenu, sender = message.split(";")
                if sender != name.decode("utf-8"):
                    print(f"{sender}: {contenu}")
        except ValueError:
            if message == "READY":
                pass
            else:
                print("Erreur de format du message reçu.")
        except KeyboardInterrupt:
            print("\nDéconnexion du serveur.")
            serv_socket.send("!quit".encode("utf-8"))
            serv_socket.close()
            break
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