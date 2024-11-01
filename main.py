from kivy.lang import Builder
from kivy.core.window import Window
import qrcode
import re
from kivymd.uix.screenmanager import MDScreenManager
from screen_classes import *
import sokect_ter as st
import chiffrer as cr
import database

# Définir la taille de la fenêtre de l'application
Window.size = (350, 650)


# Classe du gestionnaire d'écrans
class screen_manager(MDScreenManager):
    pass


# Classe principale de l'application : écran d'accueil
class main(MDApp):
    def __init__(self, **kwargs):
        super().__init__()  # Appel au constructeur de la classe parente
        # Initialisation des variables
        self.previous = {}
        self.dic = {}
        self.demande_lst = []

        # Informations sur le serveur
        self.pseudo_s = None
        self.desc_s = None
        self.port_s = None
        self.n_s = None

        # Informations sur le client
        self.ip_c = 'localhost'
        self.pseudo_c = None
        self.desc_c = None
        self.port_c = 12348

        # Variables d'erreur
        self.error_port = None
        self.error_n = None
        self.error_desc = None
        self.error_ip = None
        self.error_pseudo = None

        # Statuts de l'utilisateur
        self.disc_user = None
        self.cry_status = None

        # Gestionnaires de serveur et de client
        self.client_handler = None
        self.server_handler = None

        # Utilisateur connecté
        self.connected_user = ""
        self.message_status = None

        # Gestion de la sécurité des messages
        self.crypter = cr.MessageSecurity()
        self.crypter.generate_rsa_keys()  # Génération des clés publique et privée
        self.pri = self.crypter.private_key
        self.pub = self.crypter.public_key  # Clé publique en binaire
        self.aes_cli = {}

        # Gestion de la base de données
        self.db = database.DatabaseManager("bud.db")
        self.db.connect()
        self.db.create_table()

    def initial_server(self):
        self.previous = {}
        self.dic = {}
        self.demande_lst = []

        # Informations sur le serveur
        self.pseudo_s = None
        self.desc_s = None
        self.port_s = None
        self.n_s = None

        # Informations sur le client
        self.ip_c = 'localhost'
        self.pseudo_c = None
        self.desc_c = None
        self.port_c = 12348

        # Variables d'erreur
        self.error_port = None
        self.error_n = None
        self.error_desc = None
        self.error_ip = None
        self.error_pseudo = None

        # Statuts de l'utilisateur
        self.disc_user = None
        self.cry_status = None

        # Gestionnaires de serveur et de client

        # Utilisateur connecté
        self.connected_user = ""
        self.message_status = None


        s4 = self.root.get_screen('screen_4')
        s5 = self.root.get_screen('screen_5')

        s4.hmac_value = None  # Valeur HMAC pour la sécurité
        s4.receiver = None  # Récepteur de message
        s4.listen_thread = None  # Thread d'écoute
        s4.msg_sortie = None  # Messages à afficher
        s4.user = None  # Utilisateur actuel
        s4.sender = None  # Expéditeur du message
        s4.msg_en = None  # Message chiffré
        s4.query = None  # Requête SQL pour récupérer les messages
        s4.iv = None  # IV pour le chiffrement
        s4.msg = None  # Message à traiter

        s5 .u_pub = None  # Clé publique de l'utilisateur
        s5 .dialog = None  # Dialogue pour les descriptions
        s5 .dic_u_pub = {}  # Dictionnaire pour stocker les clés publiques des utilisateurs
        s5 .user = None  # Nom de l'utilisateur sélectionné
        s5 .previous_clients = {}  # Pour stocker la liste précédente des clients
        s5 .update_interval = 1  # Intervalle de mise à jour en secondes
        s5 .first_run = True  # Drapeau pour le premier démarrage
        s5 .user_accept = []  # Liste des utilisateurs acceptés

    def initial_client(self, user):
        s5 = self.root.get_screen('screen_5')
        if user in s5.dic_u_pub:
            del s5.dic_u_pub[user]
        if user in s5.previous_clients:
            del s5.previous_clients[user]
        if user in s5.user_accept:
            s5.user_accept.remove(user)
        if user in self.demande_lst:
            self.demande_lst.remove(user)
        if user in self.aes_cli:
            del self.aes_cli[user]




    def initial_conn(self):
        self.message_status = None

        self.ip_c = 'localhost'
        self.pseudo_c = None
        self.desc_c = None
        self.port_c = 12348
        self.connected_user = ""

        s4 = self.root.get_screen('screen_4')
        s5 = self.root.get_screen('screen_5')

        self.previous = {}
        self.dic = {}
        self.demande_lst = []

        # Statuts de l'utilisateur
        self.disc_user = None
        self.cry_status = None

        s4.hmac_value = None  # Valeur HMAC pour la sécurité
        s4.app = MDApp.get_running_app()  # Obtenir l'application en cours d'exécution
        s4.receiver = None  # Récepteur de message
        s4.listen_thread = None  # Thread d'écoute
        s4.msg_sortie = None  # Messages à afficher
        s4.user = None  # Utilisateur actuel
        s4.sender = None  # Expéditeur du message
        s4.msg_en = None  # Message chiffré
        s4.query = None  # Requête SQL pour récupérer les messages
        s4.iv = None  # IV pour le chiffrement
        s4.msg = None  # Message à traiter

        s5.u_pub = None  # Clé publique de l'utilisateur
        s5.dialog = None  # Dialogue pour les descriptions
        s5.user = None  # Nom de l'utilisateur sélectionné
        s5.update_interval = 1  # Intervalle de mise à jour en secondes
        s5.first_run = True  # Drapeau pour le premier démarrage

    def build(self):
        # Chargement des fichiers KV pour les différentes écrans
        Builder.load_file("classes_import.kv")
        Builder.load_file("screen_1.kv")
        Builder.load_file("screen_2_1.kv")
        Builder.load_file("screen_2_2.kv")
        Builder.load_file("screen_3.kv")
        Builder.load_file("screen_4.kv")
        Builder.load_file("screen_5.kv")

        # Création et ajout des écrans au gestionnaire d'écrans
        sm = MDScreenManager()
        sm.add_widget(screen1(name="screen_1"))
        sm.add_widget(screen2_1(name="screen_2_1"))
        sm.add_widget(screen2_1_1(name="screen_2_1_1"))
        sm.add_widget(screen2_2(name="screen_2_2"))
        sm.add_widget(scann(name="scann"))
        sm.add_widget(screen3(name="screen_3"))
        sm.add_widget(screen4(name="screen_4"))
        sm.add_widget(screen5(name="screen_5"))

        # Définition des thèmes de l'application
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "A700"
        self.theme_cls.theme_style = "Light"

        return sm

    def start_server(self):
        # Récupération des champs d'entrée du serveur
        s2_1 = self.root.get_screen('screen_2_1')
        self.pseudo_s = s2_1.ids.pseudo.ids.text_field
        self.desc_s = s2_1.ids.desc.ids.text_field
        self.n_s = s2_1.ids.n.ids.text_field
        self.port_s = s2_1.ids.port.ids.text_field

        # Vérification des entrées
        self.verification(id="server", pseudo=self.pseudo_s, desc=self.desc_s, port=self.port_s, n=self.n_s)
        if all([self.pseudo_s.text.strip(), self.desc_s.text.strip(), self.port_s.text.strip(), self.n_s.text.strip()]):
            if not (
                    self.error_pseudo or self.error_port or self.error_desc or self.error_n):
                # Démarrer le gestionnaire de serveur
                self.server_handler = st.ServerHandler(int(self.port_s.text), int(self.n_s.text))
                threading.Thread(target=self.server_handler.start_server, daemon=True).start()
                s2_1_1 = self.root.get_screen('screen_2_1_1')
                # Mise à jour de l'interface avec les informations du serveur
                s2_1_1.ids.pseudo.text = self.pseudo_s.text
                s2_1_1.ids.desc.text = self.desc_s.text
                s2_1_1.ids.ip.text = self.server_handler.host
                s2_1_1.ids.port.text = self.port_s.text
                s2_1_1.ids.n.text = self.n_s.text
                self.generate_qr_code()
                self.crypter.generate_aes_key()  # Génération de la clé AES
                self.first_thread()  # Démarrer le thread de mise à jour
                self.root.current = "screen_2_1_1"  # Passer à l'écran suivant

            else:
                # Notification d'erreur
                title = "échec d'activation"
                msg = "Vérifiez les champs de saisie"
                self.notificate(title, msg)
        else:
            # Notification d'erreur si des champs sont vides
            title = "échec d'activation"
            msg = "veillez remplir toutes les cases"
            self.notificate(title, msg)

    def stop_server(self):
        # Arrêter le serveur
        self.server_handler.stop_server()
        print("fait")
        self.initial_server()
        print("2")
        self.root.current = "screen_1"  # Passer à l'écran suivant
        print("3")

    def first_thread(self, *args):
        # Fonction pour ajouter des clients
        def add_client(dt):
            self.dic = self.server_handler.pseudo_ip
            if self.dic:
                self.previous = self.dic
                Clock.schedule_once(lambda dt: self.update(self.previous))
            elif self.previous != self.dic:
                Clock.schedule_once(lambda dt: self.update(self.previous))
                self.previous = self.dic
            else:
                pass

        # Vérifie l'ajout de clients toutes les secondes
        def check_thread():
            Clock.schedule_interval(add_client, 1)

        threading.Thread(target=check_thread, daemon=True).start()

    def update(self, dic):
        # Met à jour la liste des clients connectés
        s2_1_1 = self.root.get_screen('screen_2_1_1')
        s2_1_1.ids.client_list.clear_widgets()
        for user in dic.keys():
            # Création d'une carte pour chaque utilisateur
            user_card = MDCard(
                orientation="horizontal",
                size_hint=(1, None),
                height="40dp",
                padding="8dp",
                spacing="12dp",
                radius=[0, 0, 0, 0],  # Coins non arrondis
                md_bg_color=(0.9, 0.9, 0.9, 1),  # Couleur de fond pour la carte
            )

            # Label pour le nom de l'utilisateur
            user_label = MDLabel(
                text=user.split(':')[0],
                halign="left",
                size_hint_x=0.3
            )

            user_card.add_widget(user_label)  # Ajouter le label à la carte
            s2_1_1.ids.client_list.add_widget(user_card)  # Ajouter la carte à la liste

    def generate_qr_code(self):
        # Générer un QR code avec les informations du serveur
        self.ip_s = self.server_handler.host
        server_info = f"{self.ip_s}:{self.port_s.text}"  # Création de la chaîne contenant l'IP et le port
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(server_info)  # Ajout des données au QR code
        qr.make(fit=True)

        # Créer une image du QR code
        img = qr.make_image(fill='black', back_color='white')
        img.save("server_qr_code.png")  # Sauvegarde de l'image

    def add_client_to_list(self, client_name):
        # Ajouter le nom du client connecté à la liste
        new_client = OneLineListItem(text=client_name)
        screen = self.root.get_screen('screen3')
        screen.ids.clients_list.add_widget(new_client)


    def connect_client(self):
        # Récupérer les éléments de l'interface utilisateur à partir de l'écran 2_2
        s2_2 = self.root.get_screen('screen_2_2')
        self.pseudo_c = s2_2.ids.pseudo.ids.text_field  # Champ de texte pour le pseudo
        self.desc_c = s2_2.ids.desc.ids.text_field  # Champ de texte pour la description
        self.port_c = s2_2.ids.port.ids.text_field  # Champ de texte pour le port
        self.ip_c = s2_2.ids.ip.ids.text_field  # Champ de texte pour l'IP

        # Vérification des champs de saisie
        self.verification(id="client", pseudo=self.pseudo_c, desc=self.desc_c, ip=self.ip_c, port=self.port_c)

        # Vérifier si tous les champs de saisie sont remplis
        if all([self.pseudo_c.text.strip(), self.desc_c.text.strip(), self.port_c.text.strip(),
                self.ip_c.text.strip()]):

            # Vérifier l'absence d'erreurs dans les champs
            if not (self.error_pseudo or self.error_ip or self.error_port or self.error_desc):
                # Créer une instance de ClientHandler pour gérer la connexion
                self.client_handler = st.ClientHandler(self.ip_c.text, int(self.port_c.text))
                # Préparer les informations à envoyer au serveur
                info_p = self.pseudo_c.text + ":" + self.desc_c.text + ":" + self.pub.decode()
                # Tenter de se connecter au serveur
                self.client_handler.connect_to_server(info_p)

                # Vérifier si la connexion a réussi
                if self.client_handler.connected:
                    # Accéder aux écrans nécessaires après une connexion réussie
                    s5 = self.root.get_screen('screen_5')
                    s3 = self.root.get_screen('screen_3')
                    s5.verification()  # Vérification des utilisateurs acceptés
                    s5.check_for_updates()  # Vérification des mises à jour
                    s3.start_update_thread()  # Démarrer le fil d'actualisation pour les messages
                    self.root.get_screen('screen_4').start_listening()  # Démarrer l'écoute sur l'écran de chat
                    self.demander()  # Gérer les demandes de connexion des utilisateurs
                    # Démarrer un fil pour récupérer les clés AES
                    threading.Thread(target=self.recup_aes, daemon=True).start()
                    # Changer l'écran actif pour l'écran 5
                    self.root.current = "screen_5"
                else:
                    # Notification d'échec de connexion au serveur
                    title = "échec de connexion serveur"
                    msg = "le client n'est pas connecté au serveur"
                    self.notificate(title, msg)
            else:
                # Notification en cas d'erreurs dans les champs de saisie
                title = "échec de connexion serveur"
                msg = "Vérifiez les champs de saisie"
                self.notificate(title, msg)
        else:
            # Notification si des champs de saisie sont vides
            title = "échec de connexion serveur"
            msg = "Veuillez remplir les champs de saisie"
            self.notificate(title, msg)

    def disconnect_client(self):
        # Déconnecte le client et réinitialise les listes et dictionnaires associés.
        self.client_handler.close_socket()  # Ferme le socket du client.
        self.initial_client(self.pseudo_c.text)
        self.initial_conn()
        self.root.current = "screen_2_2"  # Passer à l'écran suivant

    def recup_aes(self):
        # Récupère les clés AES des utilisateurs connectés.
        while self.client_handler.connected:
            msg = self.client_handler.reponsa  # Récupère le message du client.
            if msg:
                # Sépare le message en la clé AES encodée et le nom d'utilisateur.
                msg_a, user = msg.split(':')
                en_aes = base64.b64decode(msg_a)  # Décode la clé AES depuis Base64.
                de_aes = self.crypter.decrypt_aes_key(self.pri, en_aes)  # Décrypte la clé AES.
                self.aes_cli[user] = de_aes  # Stocke la clé AES pour l'utilisateur.
                self.client_handler.reponse = None  # Réinitialise la réponse.
            else:
                pass  # Si aucun message, rien à faire.

    def notificate(self, title, msg):
        # Envoie une notification avec un titre et un message spécifiés.
        notification.notify(
            title=title,
            message=msg,
            app_name="ChatLPSIC",
            app_icon=None,  # Vous pouvez spécifier le chemin vers une icône (.ico, .png).
            timeout=50  # Temps en secondes avant que la notification ne disparaisse.
        )


    def send_message(self):
        # Envoie un message au client connecté.
        chat_screen = self.root.get_screen('screen_4')  # Accède à l'écran de chat.
        input_text = chat_screen.ids.text_input.text  # Récupère le texte saisi.
        chat_screen.ids.text_input.text = ""  # Vide le champ de texte après l'envoi.
        message_pre = "message:" + self.connected_user + ":" + self.pseudo_c.text + ":" + input_text
        if self.message_status == "No Crypter":
            # Si le message n'est pas chiffré.
            self.cry_status = "non"
            message_a_envoyer = message_pre + ":" + self.cry_status + ":" + "hmac" + ":" + "iv"
            chat_screen.afficher(input_text, "me")  # Affiche le message dans le chat.
            self.client_handler.send_message(message_a_envoyer)  # Envoie le message au client.
            self.db.store_message("me", self.connected_user, self.cry_status,
                                  input_text)  # Stocke le message dans la base de données.
        else:
            # Si le message est chiffré.
            self.cry_status = "oui"
            ciphertext, hmac_value, iv = self.crypter.encrypt_message(input_text, self.aes_cli[
                self.connected_user])  # Chiffre le message.
            message_a_envoyer = "message:" + self.connected_user + ":" + self.pseudo_c.text + ":" + base64.b64encode(
                ciphertext).decode('utf-8') + ":" + self.cry_status + ":" + base64.b64encode(hmac_value).decode(
                'utf-8') + ":" + base64.b64encode(iv).decode('utf-8')
            chat_screen.afficher(input_text, "me")  # Affiche le message dans le chat.
            self.db.store_message("me", self.connected_user, self.cry_status,
                                  input_text)  # Stocke le message dans la base de données.
            print("msg")  # Pour le débogage.
            self.client_handler.send_message(message_a_envoyer)  # Envoie le message chiffré.
            print("fait")  # Pour le débogage.

    def switch_to_screen(self, screen_name):
        # Change l'écran courant vers l'écran spécifié par name.
        self.root.current = screen_name

    def demander(self):
        # Demande des informations au serveur sur les utilisateurs connectés.
        def check_demande(dt):
            msg = self.client_handler.demande  # Récupère la demande du client.
            if msg and msg not in self.demande_lst:
                Clock.schedule_once(
                    lambda dt: self.add_user_request(msg))  # Ajoute la demande si elle n'est pas déjà présente.
                self.client_handler.demande = None  # Réinitialise la demande.

        def demander_thread():
            Clock.schedule_interval(check_demande, 1)  # Vérifie les demandes toutes les secondes.

        threading.Thread(target=demander_thread, daemon=True).start()  # Lance le thread pour vérifier les demandes.

    def add_user_request(self, user):
        # Ajoute une demande d'utilisateur dans l'interface.
        self.notificate("Discussion", "nouvelle suggestion")  # Notifie qu'il y a une nouvelle demande.
        self.disc_user = user  # Stocke l'utilisateur en attente.

        user_card = MDCard(
            orientation="horizontal",
            size_hint=(1, None),
            height="50dp",
            padding="4dp",
            spacing="6dp",
            radius=[0, 0, 0, 0],
            md_bg_color=(0.9, 0.9, 0.9, 1),  # Définit la couleur de fond de la carte.
        )

        user_label = MDLabel(
            text=user,
            halign="left",
            size_hint_x=0.5
        )

        accept_button = MDFillRoundFlatButton(
            text="Accepter",
            size_hint=(None, None),
            size=("100dp", "40dp"),
            padding=("8dp", "4dp"),
            on_release=lambda x: self.accepter(user, user_card),  # Appelle la méthode pour accepter la demande.
        )

        refuse_button = MDFillRoundFlatButton(
            text="Refuser",
            size_hint=(None, None),
            size=("100dp", "40dp"),
            padding=("8dp", "4dp"),
            on_release=lambda x: self.refuser(),  # Appelle la méthode pour refuser la demande.
        )

        user_card.add_widget(user_label)  # Ajoute le label de l'utilisateur à la carte.
        user_card.add_widget(accept_button)  # Ajoute le bouton d'acceptation à la carte.
        user_card.add_widget(refuse_button)  # Ajoute le bouton de refus à la carte.

        screenn5 = self.root.get_screen("screen_5")  # Accède à l'écran 5.
        screenn5.ids.request_container.add_widget(user_card)  # Ajoute la carte de demande à l'interface.
        self.demande_lst.append(user)  # Ajoute l'utilisateur à la liste des demandes.

    def accepter(self, msg, user_card):
        # Accepte une demande d'utilisateur et met à jour l'interface.
        screen5 = self.root.get_screen('screen_5')

        if msg not in screen5.user_accept:
            screen5.user_accept.append(msg)  # Ajoute l'utilisateur à la liste des utilisateurs acceptés.
            self.message_retour("accepté")  # Envoie une réponse d'acceptation.

            # Supprime les boutons "Accepter" et "Refuser".
            accept_button = user_card.children[1]
            refuse_button = user_card.children[0]

            user_card.remove_widget(accept_button)  # Supprime le bouton d'acceptation.
            user_card.remove_widget(refuse_button)  # Supprime le bouton de refus.

            # Ajoute le bouton "Retirer".
            retirer_button = MDFillRoundFlatButton(
                text="Retirer",
                size_hint=(None, None),
                size=("100dp", "40dp"),
                padding=("8dp", "4dp"),
                on_release=lambda x: self.retirer(msg, user_card),  # Appelle la méthode pour retirer l'utilisateur.
            )
            user_card.add_widget(retirer_button)  # Ajoute le bouton "Retirer" à la carte.

    def retirer(self, msg, user_card):
        # Retire un utilisateur de la liste des acceptés.
        screen5 = self.root.get_screen('screen_5')
        self.initial_client(msg)
        screen5.ids.request_container.remove_widget(user_card)  # Retire la carte de la demande de l'interface.
        self.message_retour(f"{msg} retiré")  # Envoie un message de retrait.

    def message_retour(self, msg):
        # Envoie un message de retour au client connecté.
        msg_r = "reponse:" + self.disc_user + ":" + msg + ":" + self.pseudo_c.text
        self.client_handler.send_message(msg_r)  # Envoie le message au client.

    def refuser(self):
        # Refuse une demande d'utilisateur.
        self.message_retour("refusé")  # Envoie une réponse de refus.

    def verification(self, **kwargs):
        global ip, n  # Déclaration des variables globales 'ip' et 'n'

        # Expressions régulières pour valider les entrées
        pattern_port = r"^([4-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"  # Plage de ports: 49152-65535
        pattern_ip = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"  # Format d'adresse IP
        pattern_pseudo = r"^[a-zA-Z0-9]*$"  # Pseudo: lettres et chiffres uniquement
        pattern_desc = r"^[\w\s.,;:?!'\"-]{1,1000}$"  # Description: caractères alphanumériques, espaces et ponctuation
        pattern_n = r"^(?:[2-9]|1[0-6])$"  # Valeur numérique entre 2 et 16

        # Initialisation des erreurs
        self.error_n = self.error_pseudo = self.error_desc = self.error_ip = self.error_port = False

        # Récupérer les valeurs des arguments passés
        if kwargs.get('id') == "server":  # Vérification si l'identifiant est "server"
            n = kwargs.get('n')  # Récupération de la valeur 'n'
            if n and re.match(pattern_n, str(n.text)):  # Validation de 'n' avec l'expression régulière
                self.error_n = False  # Pas d'erreur
                n.helper_text = ""  # Pas de message d'aide
            else:
                self.error_n = True  # Erreur de validation
                n.helper_text = "Input must be numeric (numbers only)"  # Message d'erreur
                n.helper_text_mode = "persistent"  # Mode d'affichage persistant du message

        else:  # Si l'identifiant n'est pas "server"
            ip = kwargs.get('ip')  # Récupération de l'adresse IP
            if ip and re.match(pattern_ip, ip.text):  # Validation de l'adresse IP
                self.error_ip = False  # Pas d'erreur
                ip.helper_text = ""  # Pas de message d'aide
            else:
                self.error_ip = True  # Erreur de validation
                ip.helper_text = "Input must be integer and dot (192.168.10.5)"  # Message d'erreur
                ip.helper_text_mode = "persistent"  # Mode d'affichage persistant du message

        # Récupération des autres paramètres
        pseudo = kwargs.get('pseudo')  # Récupération du pseudo
        desc = kwargs.get('desc')  # Récupération de la description
        port = kwargs.get('port')  # Récupération du port

        # Validation du pseudo
        if pseudo and re.match(pattern_pseudo, pseudo.text):
            self.error_pseudo = False  # Pas d'erreur
            pseudo.helper_text = ""  # Pas de message d'aide
        else:
            self.error_pseudo = True  # Erreur de validation
            pseudo.helper_text = "Input must be alphanumeric (letters and numbers only)"  # Message d'erreur
            pseudo.helper_text_mode = "persistent"  # Mode d'affichage persistant du message

        # Validation de la description
        if desc and re.match(pattern_desc, desc.text):
            self.error_desc = False  # Pas d'erreur
            desc.helper_text = ""  # Pas de message d'aide
        else:
            self.error_desc = True  # Erreur de validation
            desc.helper_text = "Input must be alphanumeric (letters and numbers only)"  # Message d'erreur
            desc.helper_text_mode = "persistent"  # Mode d'affichage persistant du message

        # Validation du port
        if port and re.match(pattern_port, port.text):
            self.error_port = False  # Pas d'erreur
            port.helper_text = ""  # Pas de message d'aide
        else:
            self.error_port = True  # Erreur de validation
            port.helper_text = "Input must be integer (49152-65535)"  # Message d'erreur
            port.helper_text_mode = "persistent"  # Mode d'affichage persistant du message

    def change_color(self, card, new_color):
        # Change la couleur d'arrière-plan de la carte à 'new_color'
        card.md_bg_color = new_color


if __name__ == '__main__':
    main().run()
