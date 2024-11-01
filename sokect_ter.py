
import socket
import threading
import json

class ServerHandler:
    def __init__(self, port, n):
        """Initialise le gestionnaire de serveur avec le port et le nombre maximum de connexions.

        Args:
            port (int): Le port sur lequel le serveur écoutera les connexions.
            n (int): Le nombre maximum de connexions simultanées autorisées.
        """
        self.t1 = None  # Thread pour accepter les clients
        self.t2 = None  # Thread pour gérer un client
        self.client_threads = []  # Liste des threads de clients
        self.user = ""  # Pseudonyme de l'utilisateur
        self.message = ""  # Message à traiter
        self.receiver = ""  # Destinataire du message
        self.addr = ""  # Adresse IP du client
        self.host = self.get_ip()  # Obtient l'adresse IP du serveur
        self.n = n  # Nombre maximum de connexions
        self.port = port  # Port sur lequel le serveur écoute
        self.server_socket = None  # Socket du serveur
        self.clients = []  # Liste des sockets des clients connectés
        self.pseudo = []  # Liste des pseudonymes des clients
        self.cli_pseudo = {}  # Dictionnaire associant les pseudonymes aux sockets des clients
        self.pseudo_ip = {}  # Dictionnaire associant les pseudonymes aux adresses IP
        self.running = False  # Indicateur d'état du serveur

    def get_ip(self):
        """Obtient l'adresse IP locale du serveur."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Crée un socket UDP
        s.settimeout(0)  # Définit un délai d'attente
        try:
            s.connect(('10.254.254.254', 1))  # Tente de se connecter à une adresse IP externe
            IP = s.getsockname()[0]  # Obtient l'adresse IP utilisée
        except Exception:
            IP = '127.0.0.1'  # Si l'adresse IP ne peut pas être déterminée, utilise localhost
        finally:
            s.close()  # Ferme le socket
        return IP  # Retourne l'adresse IP

    def start_server(self):
        """Démarre le serveur et commence à accepter les connexions des clients."""
        if self.running:  # Vérifie si le serveur est déjà en cours d'exécution
            return
        self.running = True  # Met à jour l'indicateur d'état pour démarrer le serveur
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crée un socket TCP
        self.server_socket.bind((self.host, self.port))  # Lie le socket à l'adresse IP et au port
        self.server_socket.listen(self.n)  # Commence à écouter les connexions
        self.t1 = threading.Thread(target=self.accept_clients, daemon=True)  # Démarre le thread pour accepter les clients
        self.t1.start()  # Lance le thread
        print("Serveur démarré sur {}:{}".format(self.host, self.port))  # Affiche les informations de démarrage

    def accept_clients(self):
        """Accepte les connexions des clients en boucle."""
        while self.running:  # Continue tant que le serveur est en cours d'exécution
            try:
                client_socket, self.addr = self.server_socket.accept()  # Accepte une nouvelle connexion
                if client_socket not in self.clients:  # Vérifie si le client est déjà connecté
                    self.clients.append(client_socket)  # Ajoute le client à la liste
                self.t2 = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)  # Crée un thread pour gérer le client
                if self.t2 not in self.client_threads:  # Vérifie si le thread n'est pas déjà dans la liste
                    self.client_threads.append(self.t2)  # Ajoute le thread à la liste
                self.t2.start()  # Lance le thread
            except Exception as e:
                break  # Sort de la boucle en cas d'erreur

    def handle_client(self, client_socket):
        """Gère la communication avec un client connecté."""
        buffer = ""  # Tampon pour stocker les données reçues
        while self.running:  # Continue tant que le serveur est en cours d'exécution
            try:
                data = client_socket.recv(2 * 1024).decode()  # Reçoit les données du client
                if not data:  # Si aucune donnée n'est reçue, quitte la boucle
                    break

                buffer += data  # Ajoute les données au tampon
                while "<START>" in buffer and "<END>" in buffer:  # Vérifie si un message complet est dans le tampon
                    start_index = buffer.find("<START>") + len("<START>")  # Trouve le début du message
                    end_index = buffer.find("<END>")  # Trouve la fin du message
                    if end_index > start_index:  # Si les indices sont valides
                        message = buffer[start_index:end_index]  # Extrait le message du tampon
                        self.process_message(message, client_socket)  # Traite le message
                        buffer = buffer[end_index + len("<END>"):]  # Met à jour le tampon

            except Exception as e:
                # Gestion des erreurs lors de la réception des données
                if client_socket in self.pseudo:
                    self.pseudo.remove(client_socket)  # Retire le socket de la liste des pseudonymes
                if client_socket in self.clients:
                    self.clients.remove(client_socket)  # Retire le socket de la liste des clients
                if client_socket in self.client_threads:
                    self.client_threads.remove(client_socket)  # Retire le thread de la liste
                if client_socket in self.cli_pseudo:
                    self.cli_pseudo = {k: v for k, v in self.cli_pseudo.items() if v != client_socket}  # Retire le socket du dictionnaire
                if client_socket in self.pseudo_ip:
                    self.pseudo_ip = {k: v for k, v in self.pseudo_ip.items() if v != client_socket}  # Retire le socket du dictionnaire
                client_socket.close()  # Ferme le socket du client
                break  # Quitte la boucle
        client_socket.close()  # Ferme le socket du client

    def process_message(self, message, client_socket):
        """Traite le message reçu d'un client.

        Args:
            message (str): Le message à traiter.
            client_socket: Le socket du client qui a envoyé le message.
        """
        parts = message.split(':', 1)  # Divise le message en deux parties
        command, content = parts[0], parts[1]  # Extrait la commande et le contenu

        if command == "info_p":  # Commande pour définir le pseudonyme
            parts = content.split(':', 1)  # Divise le contenu pour obtenir le pseudonyme
            user = parts[0]  # Récupère le pseudonyme
            if user not in self.cli_pseudo:  # Si le pseudonyme n'est pas déjà associé
                self.cli_pseudo[user] = client_socket  # Associe le pseudonyme au socket
                self.pseudo_ip[content] = self.addr  # Associe le pseudonyme à l'adresse IP
                msg = "info_p:" + json.dumps(self.pseudo_ip)  # Crée un message avec les informations des pseudonymes
                self.broadcast(msg)  # Diffuse le message à tous les clients

        elif command == "ajouter":  # Commande pour ajouter un contact
            paquet = content.split(':', 1)  # Divise le contenu en deux parties
            receiver_pseudo, sender = paquet[0], paquet[1]  # Récupère le pseudonyme du destinataire et de l'expéditeur
            msg = "demander:" + sender  # Crée un message de demande
            self.envoyer(receiver_pseudo, msg)  # Envoie le message au destinataire

        elif command == "reponse":  # Commande pour envoyer une réponse
            paquet = content.split(':', 1)  # Divise le contenu en deux parties
            receiver_pseudo, retour = paquet[0], paquet[1]  # Récupère le pseudonyme du destinataire et le retour
            msg = "resultat:" + retour  # Crée un message de résultat
            self.envoyer(receiver_pseudo, msg)  # Envoie le message au destinataire

        elif command == "repons":  # Commande similaire à "reponse" mais peut-être pour un autre type de réponse
            paquet = content.split(':', 1)  # Divise le contenu
            receiver_pseudo, retour = paquet[0], paquet[1]  # Récupère les valeurs
            msg = "resultata:" + retour  # Crée un message de résultat
            self.envoyer(receiver_pseudo, msg)  # Envoie le message au destinataire

        elif command == "message":  # Commande pour envoyer un message
            paquet = content.split(':', 1)  # Divise le contenu
            receiver_pseudo, msg = paquet[0], paquet[1]  # Récupère le destinataire et le message
            self.envoyer(receiver_pseudo, msg)  # Envoie le message au destinataire

    def broadcast(self, message):
        """Diffuse un message à tous les clients connectés.

        Args:
            message (str): Le message à diffuser.
        """
        for client in self.clients:  # Itère sur tous les clients
            try:
                client.sendall(("<START>" + message + "<END>").encode())  # Envoie le message au client
            except Exception:
                client.close()  # Ferme le socket en cas d'erreur

    def envoyer(self, pseudo_dest, message):
        """Envoie un message à un destinataire spécifique.

        Args:
            pseudo_dest (str): Le pseudonyme du destinataire.
            message (str): Le message à envoyer.
        """
        if pseudo_dest in self.cli_pseudo:  # Vérifie si le destinataire est dans le dictionnaire
            try:
                self.cli_pseudo[pseudo_dest].sendall(("<START>" + message + "<END>").encode())  # Envoie le message
            except Exception:
                self.cli_pseudo[pseudo_dest].close()  # Ferme le socket en cas d'erreur

    def stop_server(self):
        """Arrête le serveur et ferme toutes les connexions clients."""
        self.running = False  # Met à jour l'indicateur pour arrêter le thread
        for client in self.clients:
            client.close()  # Ferme chaque socket client
        if self.server_socket:
            self.server_socket.close()  # Ferme le socket du serveur
        self.reset_values()  # Réinitialiser toutes les valeurs

    def reset_values(self):
        """Réinitialiser toutes les valeurs du serveur."""
        self.t1 = None
        self.t2 = None
        self.client_threads = []
        self.user = ""
        self.message = ""
        self.receiver = ""
        self.addr = ""
        self.clients = []
        self.pseudo = []
        self.cli_pseudo = {}
        #self.pseudo_ip = {}
        self.running = False


class ClientHandler:
    def __init__(self, host, port):
        self.reponsa = None
        self.t = None
        self.reponse = None
        self.demande = None
        self.pseudo_ip = {}
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.msg = None

    def connect_to_server(self, info_p):
        """Connecte le client au serveur et envoie le pseudonyme."""
        try:
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            self.send_message(f"info_p:{info_p}")  # Envoie le pseudonyme au serveur
            self.t = threading.Thread(target=self.receive_messages, daemon=True)
            self.t.start()
        except Exception as e:
            print(f"Failed to connect: {e}")

    def receive_messages(self):
        """Reçoit des messages du serveur."""
        buffer = ""
        while self.connected:
            try:
                data = self.client_socket.recv(2048).decode()
                buffer += data
                while "<START>" in buffer and "<END>" in buffer:
                    start_index = buffer.find("<START>") + len("<START>")
                    end_index = buffer.find("<END>")
                    if end_index > start_index:
                        message = buffer[start_index:end_index]
                        self.process_message(message)
                        buffer = buffer[end_index + len("<END>"):]
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.connected = False
        self.close_socket()

    def process_message(self, message):
        """Traite le message reçu du serveur."""
        parts = message.split(':', 1)
        command = parts[0]
        content = parts[1] if len(parts) > 1 else ""

        if command == "info_p":
            self.pseudo_ip = json.loads(content)
        elif command == "demander":
            self.demande = content
        elif command == "resultat":
            self.reponse = content
        elif command == "resultata":
            self.reponsa = content
        else:
            self.msg = message
            print("Message reçu :", message)

    def send_message(self, message):
        """Envoie un message au serveur."""
        if self.connected:
            try:
                msg_with_ids = f"<START>{message}<END>"
                self.client_socket.send(msg_with_ids.encode())
            except Exception as e:
                print(f"Error sending message: {e}")

    def close_socket(self):
        """Ferme la connexion du client."""
        if self.connected:
            try:
                self.client_socket.close()
                self.connected = False
                print("Socket fermé correctement.")
            except OSError as e:
                if e.errno == 9:  # Mauvais descripteur de fichier, le socket est déjà fermé
                    print("Le socket est déjà fermé.")
                else:
                    print(f"Erreur inattendue lors de la fermeture du socket: {e}")
        self.reset_values()

    def reset_values(self):
        """Réinitialise les valeurs du client."""
        self.t = None
        self.reponse = None
        self.demande = None
        self.pseudo_ip = {}
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.msg = None
