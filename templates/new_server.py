import os
import json
import shutil
import time

print("Bienvenue sur l'assitant de création de serveur de communication !")

print("Veuillez entrer le nom de votre serveur :")
name = input(">>> ")
time.sleep(0.1)
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
time.sleep(0.1)

conf_path = os.path.abspath(conf_path)
if not os.path.exists(conf_path):
    os.makedirs(conf_path)

print(f"Les fichiers de configuration seront enregistrés dans : {conf_path}")
shutil.copyfile("templates/serveur.py", os.path.join(conf_path, "serveur.py"))
shutil.copyfile("templates/sendX.py", os.path.join(conf_path, "sendX.py"))
shutil.copyfile("client.py", os.path.join(conf_path, "client.py"))
shutil.copyfile("README.md", os.path.join(conf_path, "README.md"))
shutil.copyfile("LICENCE.txt", os.path.join(conf_path, "LICENCE.txt"))

with open(os.path.join(conf_path, "launch.bat"), "w") as f:
    f.write(f"python {os.path.abspath(os.path.join(conf_path, 'serveur.py'))}")
with open(os.path.join(conf_path, "launch.sh"), "w") as f:
    f.write(f"python3 {os.path.abspath(os.path.join(conf_path, 'serveur.py'))}")

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