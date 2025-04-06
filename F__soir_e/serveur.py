from sendX import *

# Initialisation du serveur
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.bind((HOSTNAME, PORT))

print(f"Serveur '{SERVER_NAME}' ({HOSTNAME}:{PORT}) avec un buffer de {BUFFER_SIZE} octets.")
print(f"Message de bienvenue : {WELCOME_MESSAGE}")
main_socket.listen(5)


# Lancement du thread de traitement des messages
message_thread = Thread(target=process_messages, daemon=True)
message_thread.start()

# Boucle principale pour accepter les connexions
while True:
    print("En attente de connexions...")
    try:
        client, addr = main_socket.accept()
        print(f"Nouvelle connexion : {addr}")
        name = handle_new_connection(client)
        if name:
            client_thread = Thread(target=handle_client, args=(client, name), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
        break
    except Exception as e:
        print(f"Erreur dans la boucle principale : {e}")