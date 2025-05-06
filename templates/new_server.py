import os
import sys
import json
import shutil
import time
import subprocess

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return f"installation de {package} réussie"
    except:
        return f"l'installation de {package} a échouée (cela peux poser problème plus tard mais pour l'instant ne t'inquiète pas)"

print(install("ctypes"))

placeholder = {"é": "e", "è": "e", "ê": "e", "ë": "e", "ô": "o", "ö": "o", "ç": "c", "à": "a", "â": "a", "î": "i", "ï": "i", "û": "u", "ü": "u", "ô": "o", "œ": "oe", "É": "E", "È": "E", "Ê": "E", "Ë": "E", "Ô": "O", "Ö": "O", "Ç": "C", "À": "A", "Â": "A", "Î": "I", "Ï": "I", "Û": "U", "Ü": "U", "Ô": "O", "Œ": "OE"," ": "_"}


print("Bienvenue sur l'assitant de création de serveur de communication !")

name = None
while name is None or name == "":
    print("Veuillez entrer le nom de votre serveur :")
    name = input(">>> ")
    if not name:
        print("Le nom du serveur ne peut pas être vide. Veuillez réessayer.")
        time.sleep(0.1)

    else:
        for key, value in placeholder.items():
            name = name.replace(key, value)
time.sleep(0.1)

print("selctionnez un mode de configuration :")
print("1. Configuration automatique (recommandé)")
print("2. Configuration manuelle")
config_mode = input(">>> ")
if config_mode == "1":
    ip = "AUTO"
    port = 8888
    max_conn = 10
    buffer_size = 1024
    time.sleep(0.1)
if config_mode == "2":
    ip = "AUTO"

    print("Veuillez entrer l'adresse IP de votre serveur (defaut AUTO (ip privée)) :")
    ip = input(">>> ")
    if not ip:
        ip = "AUTO"
    time.sleep(0.1)

    print("Veuillez entrer le port d'écoute (defaut 8888):")
    port = input(">>> ")
    if not port:
        port = 8888
    time.sleep(0.1)

    print("Veuillez entrer le nombre de connexions maximum (defaut 10):")
    max_conn = input(">>> ")
    if not max_conn:
        max_conn = 10
    time.sleep(0.1)

    print("Veuillez entrer la taille du buffer (defaut 1024):")
    buffer_size = input(">>> ")
    if not buffer_size:
        buffer_size = 1024
    time.sleep(0.1)

print("Veuillez entrer le message de bienvenue :")
welcome_message = input(">>> ")
time.sleep(0.1)

print("où voulez-vous enregistrer les fichiers de configuration ?")
conf_path = input(">>> ")
for key, value in placeholder.items():
    conf_path = conf_path.replace(key, value)
if not conf_path:
    conf_path = os.path.join(os.getcwd(), name)
time.sleep(0.1)

conf_path = os.path.abspath(conf_path)
if not os.path.exists(conf_path):
    os.makedirs(conf_path)

print(f"Les fichiers de configuration seront enregistrés dans : {conf_path}")
print(os.path.abspath("templates/serveur.py"))
shutil.copyfile(os.path.abspath("templates/serveur.py"), os.path.join(conf_path, "serveur.py"))
shutil.copyfile(os.path.abspath("templates/sendX.py"), os.path.join(conf_path, "sendX.py"))
shutil.copyfile(os.path.abspath("client.py"), os.path.join(conf_path, "client.py"))
shutil.copyfile(os.path.abspath("README.md"), os.path.join(conf_path, "README.md"))
shutil.copyfile(os.path.abspath("LICENCE.txt"), os.path.join(conf_path, "LICENCE.txt"))

if os.name == 'nt':  # Windows
    with open(os.path.join(conf_path, "launch.bat"), "w") as f:
        f.write(f"python {os.path.abspath(os.path.join(conf_path, 'serveur.py'))}")
else:  # Unix-based systems (Linux, macOS, etc.)
    with open(os.path.join(conf_path, "launch.sh"), "w") as f:
        f.write(f"python3 {os.path.abspath(os.path.join(conf_path, 'serveur.py'))}")
        os.chmod(os.path.join(conf_path, "launch.sh"), 0o755)  # Make the script executable

with open(os.path.join(conf_path, "config.json"), "w") as f:
    json.dump({
        "HOSTNAME": ip,
        "PORT": int(port),
        "BUFFER_SIZE": int(buffer_size),
        "SERVER_NAME": name,
        "WELCOME_MESSAGE": welcome_message,
        "MAX_CONNECTIONS": int(max_conn)
    }, f, indent=4)

print("Fichiers de configuration créés avec succès !")
print("Vous pouvez maintenant lancer le serveur avec le fichier launch.bat.")
print("N'oubliez pas de lancer le client avec le fichier client.py.")
print("Merci d'avoir utilisé l'assistant de création de serveur !")
print("Appuyez sur ENTRER pour quitter.")
input()
exit()