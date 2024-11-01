from kivy.metrics import dp
import threading
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.list import OneLineListItem
import cv2
import numpy as np
import base64
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.screen import MDScreen
from plyer import notification
from classes_import import *

# Classe pour l'écran d'accueil
class screen1(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass  # Pas de logique ajoutée pour l'instant


# Classe pour un sous-écran d'accueil
class screen2_1(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass  # Pas de logique ajoutée pour l'instant


# Classe pour un autre sous-écran d'accueil
class screen2_1_1(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass  # Pas de logique ajoutée pour l'instant


# Classe pour un autre sous-écran d'accueil
class screen2_2(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass  # Pas de logique ajoutée pour l'instant


# Classe pour le scanner QR code
class scann(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass  # Pas de logique ajoutée pour l'instant

    # Méthode pour scanner un QR code
    def scan_qr_code(self, dt):
        camera = self.ids.camera  # Récupérer la caméra
        texture = camera.texture  # Obtenir la texture de la caméra

        if texture is None:
            return  # Ne rien faire si la texture est vide

        # Convertir la texture Kivy en image compatible OpenCV
        image_data = np.frombuffer(texture.pixels, np.uint8).reshape(texture.height, texture.width, 4)

        # Convertir l'image en niveaux de gris pour le traitement
        gray_image = cv2.cvtColor(image_data, cv2.COLOR_RGBA2GRAY)

        # Utiliser OpenCV pour détecter le QR code
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(gray_image)

        # Afficher le résultat si un QR code est détecté
        if data:
            self.ids.qr_result.text = f"QR Code détecté : {data}"
        else:
            self.ids.qr_result.text = "Aucun QR code détecté"

    # Méthode pour capturer une image à partir de la caméra
    def capture_image(self):
        camera = self.ids.camera
        camera.export_to_png("captured_image.png")  # Exporter l'image capturée
        # print("Image capturée et sauvegardée sous 'captured_image.png'")

# Classe pour un écran de discussion
class screen3(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass  # Pas de logique ajoutée pour l'instant

    # Démarrer un thread pour mettre à jour la liste des utilisateurs
    def start_update_thread(self):
        threading.Thread(target=self.schedule_client_updates, daemon=True).start()

    # Programmer les mises à jour de la liste des utilisateurs
    def schedule_client_updates(self):
        Clock.schedule_interval(self.update_clients, 1)  # Mise à jour toutes les secondes

    # Méthode pour mettre à jour la liste des utilisateurs
    def update_clients(self, dt=None):  # dt pour compatibilité avec Clock.schedule_interval
        app = MDApp.get_running_app()  # Obtenir l'application en cours d'exécution
        screen5 = app.root.get_screen('screen_5')  # Accéder à l'écran 5
        user_list = screen5.user_accept  # Récupérer la liste des utilisateurs

        # Mettre à jour l'interface graphique de manière sécurisée
        Clock.schedule_once(lambda dt: self.display_user_list(user_list))

    # Afficher la liste des utilisateurs
    def display_user_list(self, user_list):
        self.ids.container.clear_widgets()  # Effacer les widgets existants
        for user in user_list:
            item = OneLineListItem(text=user)  # Créer un nouvel élément de liste
            item.bind(on_release=lambda x, name=user: self.switch_to_chat_screen(name))  # Lier l'événement
            self.ids.container.add_widget(item)  # Ajouter l'élément à l'interface

    # Changer l'écran pour afficher la discussion avec un utilisateur spécifique
    def switch_to_chat_screen(self, user):
        app = MDApp.get_running_app()  # Obtenir l'application en cours d'exécution
        screen4 = app.root.get_screen('screen_4')  # Accéder à l'écran 4
        bar = screen4.ids.bar_id  # Accéder à la barre de titre de l'écran
        app.connected_user = user  # Définir l'utilisateur connecté
        screen4.user = user  # Définir l'utilisateur actuel
        lst = app.client_handler.pseudo_ip.keys()  # Obtenir la liste des utilisateurs
        #for x in lst:
        #    if user in x:
        #        app.desc = x.split(':')[1]  # Extraire la description
        bar.title = user  # Mettre à jour le titre de la barre
        self.manager.current = "screen_4"  # Changer l'écran actuel

# Classe pour l'écran de discussion
class screen4(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hmac_value = None  # Valeur HMAC pour la sécurité
        self.app = MDApp.get_running_app()  # Obtenir l'application en cours d'exécution
        self.receiver = None  # Récepteur de message
        self.listen_thread = None  # Thread d'écoute
        self.msg_sortie = None  # Messages à afficher
        self.user = None  # Utilisateur actuel
        self.sender = None  # Expéditeur du message
        self.msg_en = None  # Message chiffré
        self.query = None  # Requête SQL pour récupérer les messages
        self.iv = None  # IV pour le chiffrement
        self.msg = None  # Message à traiter

        # Items pour le menu de cryptographie
        self.crypto_menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Crypter",
                "on_release": lambda x="Crypter": self.crypt(x)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "No Crypter",
                "on_release": lambda x="No Crypter": self.crypt(x)
            },
        ]
        # Menu de cryptographie
        self.crypto_menu = MDDropdownMenu(
            items=self.crypto_menu_items,
            #width=dp(50),
            max_height=dp(140),
            radius=[14, 0, 14, 0],
            elevation=3,
        )

    # Lorsque l'écran est ouvert, récupérer les messages
    def on_enter(self, *args):
        self.recuperation()

    # Récupérer les messages de la base de données
    def recuperation(self):
        self.ids.chat_list.clear_widgets()  # Effacer la liste des messages
        self.query = '''
                SELECT sender, receiver, statut, message, timestamp 
                FROM messages 
                WHERE (sender = ? AND receiver = ?)
                    OR (sender = ? AND receiver = ?)
                ORDER BY timestamp
            '''
        # Récupérer les messages de la base de données
        self.msg_sortie = self.app.db.get_messages(self.query, (self.user, "me", "me", self.user))
        for m in self.msg_sortie:
            sender = m[0]  # Expéditeur
            msg = m[3]  # Contenu du message
            # Afficher le message en fonction de l'expéditeur
            if sender == "me":
                self.afficher(msg, "me")
            else:
                self.afficher(msg, "autre")

    # Afficher un message dans la liste de discussion
    def afficher(self, value, qui):
        if value:
            # Déterminer la taille et l'alignement du texte en fonction de sa longueur
            if len(value) < 6:
                size = .22
                halign = "center"
            elif len(value) < 11:
                size = .32
                halign = "center"
            elif len(value) < 16:
                size = .45
                halign = "center"
            elif len(value) < 21:
                size = .58
                halign = "center"
            elif len(value) < 26:
                size = .71
                halign = "center"
            else:
                size = .77
                halign = "left"

            # Ajouter le message dans la liste de discussion en fonction de son expéditeur

            if qui == "me":
                self.ids.chat_list.add_widget(Command(text=value, size_hint_x=size, halign=halign))
            else:
                self.ids.chat_list.add_widget(Response(text=value, size_hint_x=size, halign=halign))

    def start_listening(self):
        # Démarre un thread pour initier la vérification des messages en arrière-plan
        self.listen_thread = threading.Thread(target=self.schedule_message_check)
        self.listen_thread.daemon = True  # Permet au thread de se terminer lorsque l'application se ferme
        self.listen_thread.start()  # Lance le thread

    def schedule_message_check(self):
        # Programme une vérification régulière des messages toutes les 0.5 secondes
        Clock.schedule_interval(self.listen_for_messages, 1)  # Vérification chaque seconde

    def listen_for_messages(self, dt=None):
        # Essaie d'écouter les messages entrants
        try:
            message = self.app.client_handler.msg  # Récupère le message du client
            if message and message.strip():  # Vérifie si le message n'est pas vide
                self.msg = message  # Stocke le message pour le traitement
                print("oui")  # Indique que le message a été reçu
                self.process_message(self.msg)  # Traite le message reçu
                print("1")  # Indique que le message a été traité
                self.msg = None  # Réinitialise le message après traitement
                self.app.client_handler.msg = None  # Réinitialise le message dans le gestionnaire de client
        except Exception as e:
            print(f"Erreur lors de la réception du message : {e}")  # Affiche une erreur en cas d'exception

    def process_message(self, message):
        # Traite le message reçu
        try:
            separe = message.split(':')  # Sépare le message par le caractère ':'
            print("separe   :", separe)  # Affiche les parties séparées du message
            if len(separe) == 5:  # Vérifie que le message a 5 parties
                sender, msg, statut, hmac, iv = separe  # Assigne chaque partie à une variable
                if statut == "non":  # Vérifie si le statut est "non"
                    # Stocke le message dans la base de données et l'affiche
                    self.app.db.store_message(sender, self.app.connected_user, self.app.cry_status, msg)
                    Clock.schedule_once(
                        lambda dt: self.afficher(msg, "autre"))  # Affiche le message sur l'interface
                    print("ouff ")  # Indique que le message a été traité avec succès
                else:
                    # Déchiffre le message si le statut n'est pas "non"
                    self.sender = sender
                    self.ciphertext = base64.b64decode(msg)  # Décode le message chiffré
                    self.hmac_value = base64.b64decode(hmac)  # Décode la valeur HMAC
                    self.iv = base64.b64decode(iv)  # Décode le vecteur d'initialisation
                    self.receiver = "me"  # Définit le récepteur comme "moi"
                    aes = self.app.aes_cli[sender]  # Récupère la clé AES pour le sender
                    msg_af = self.decode_msg(self.ciphertext, self.hmac_value, aes, self.iv)  # Déchiffre le message
                    # Stocke le message déchiffré dans la base de données et l'affiche
                    self.app.db.store_message(self.sender, "me", self.app.cry_status, msg_af)
                    Clock.schedule_once(lambda dt: self.afficher(msg_af, "autre"))  # Affiche le message déchiffré
        except Exception as e:
            print(f"Erreur lors du traitement du message : {e}")  # Affiche une erreur en cas d'exception

    def decode_msg(self, ciphertext, hmac_value, de_aes, iv):
        # Déchiffre le message chiffré à l'aide de la clé AES
        return self.app.crypter.decrypt_message(ciphertext, hmac_value, de_aes, iv)

    def crypto(self, instance):
        # Ouvre le menu de cryptographie en fonction de l'instance qui l'a appelé
        self.crypto_menu.caller = instance
        self.crypto_menu.open()

    def crypt(self, action):
        # Définit le statut du message à partir de l'action choisie et ferme le menu de cryptographie
        self.app.message_status = action
        self.crypto_menu.dismiss()

    '''Classe du 1e Screen: écran d'accueil '''

#############
class screen5(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Appelle le constructeur de la classe parente
        self.u_pub = None  # Clé publique de l'utilisateur
        self.dialog = None  # Dialogue pour les descriptions
        self.dic_u_pub = {}  # Dictionnaire pour stocker les clés publiques des utilisateurs
        self.user = None  # Nom de l'utilisateur sélectionné
        self.previous_clients = {}  # Pour stocker la liste précédente des clients
        self.update_interval = 1  # Intervalle de mise à jour en secondes
        self.first_run = True  # Drapeau pour le premier démarrage
        self.user_accept = []  # Liste des utilisateurs acceptés

    def check_for_updates(self, *args):
        app = MDApp.get_running_app()  # Récupère l'instance de l'application en cours

        # Fonction de vérification des clients
        def check_for_clients(dt):
            current_clients = app.client_handler.pseudo_ip  # Récupère la liste actuelle des clients
            if self.first_run:  # Si c'est la première exécution
                self.previous_clients = current_clients  # Enregistre les clients actuels
                Clock.schedule_once(lambda dt: self.update_clients())  # Met à jour l'interface
                self.first_run = False  # Définit le drapeau pour indiquer que la première exécution est terminée
            elif current_clients != self.previous_clients:  # Si la liste des clients a changé
                self.previous_clients = current_clients  # Met à jour la liste précédente
                Clock.schedule_once(lambda dt: self.update_clients())  # Met à jour l'interface

        def check_thread():
            # Démarre l'intervalle pour vérifier les clients
            Clock.schedule_interval(check_for_clients, 1)  # Vérifie toutes les secondes

        # Démarrer le thread
        threading.Thread(target=check_thread, daemon=True).start()  # Lancement du thread pour la vérification

    def update_clients(self):
        self.ids.user_list.clear_widgets()  # Efface la liste d'utilisateurs actuelle
        liste = self.previous_clients  # Récupère la liste précédente des clients
        # print("fait")  # Décommenter si besoin de déboguer
        for user, info in liste.items():  # Parcourt chaque utilisateur
            user_name, desc, u_pub = user.split(':')  # Sépare les informations de l'utilisateur

            # Création d'un MDCard pour chaque utilisateur
            user_card = MDCard(
                orientation="horizontal",
                size_hint=(1, None),
                height="50dp",
                padding="8dp",
                spacing="12dp",
                radius=[0, 0, 0, 0],  # Rectangle sans coins arrondis
                md_bg_color=(0.9, 0.9, 0.9, 1),  # Optionnel : couleur de fond pour différencier les cartes
            )

            # Label pour le nom de l'utilisateur
            user_label = MDLabel(
                text=user_name,
                halign="left",
                size_hint_x=0.3  # Taille du label en proportion de la carte
            )

            # Bouton "Description" pour afficher la description dans un dialogue
            description_button = MDFillRoundFlatButton(
                text="Description",
                size_hint=(None, None),
                size=("100dp", "40dp"),
                padding=("8dp", "4dp"),
                on_release=lambda x, desc_d=desc: self.description(desc_d),
                # Appelle la méthode pour afficher la description
            )

            # Bouton "Ajouter" pour ajouter un utilisateur
            ajouter_button = MDFillRoundFlatButton(
                text="Ajouter",
                size_hint=(None, None),
                size=("80dp", "40dp"),
                padding=("8dp", "4dp"),
                on_release=lambda x, user_name_d=user_name, u_pub_d=u_pub: self.ajouter(user_name_d, u_pub_d),
                # Appelle la méthode pour ajouter l'utilisateur
            )

            # Ajout des widgets dans le MDCard
            user_card.add_widget(user_label)  # Ajoute le label à la carte
            user_card.add_widget(description_button)  # Ajoute le bouton de description à la carte
            user_card.add_widget(ajouter_button)  # Ajoute le bouton d'ajout à la carte

            # Ajout de la carte au
            self.ids.user_list.add_widget(user_card)  # Ajoute la carte à la liste d'utilisateurs


    def description(self, desc):
        # Crée une boîte de dialogue affichant la description fournie.
        self.dialog = MDDialog(
            text=desc,  # Le texte affiché dans la boîte de dialogue.
            size_hint=(0.8, .2),  # Taille relative de la boîte de dialogue.
            auto_dismiss=False,  # La boîte de dialogue ne se fermera pas automatiquement.
            buttons=[
                MDFillRoundFlatButton(
                    text="ok",  # Texte du bouton.
                    on_release=self.ok  # Action à effectuer lors du clic sur le bouton.
                ),
            ],
        )
        self.dialog.open()  # Ouvre la boîte de dialogue.

    def ok(self, *args):
        # Méthode pour fermer la boîte de dialogue.
        self.dialog.dismiss()  # Ferme la boîte de dialogue actuelle.

    def ajouter(self, user, pub):
        # Ajoute un utilisateur à la liste des contacts.
        self.user = user  # Stocke le nom de l'utilisateur.
        print("1")
        self.u_pub = pub  # Stocke la clé publique de l'utilisateur.
        print("2")
        self.dic_u_pub[user] = pub  # Ajoute la clé publique au dictionnaire des utilisateurs.
        print("3")
        app = MDApp.get_running_app()  # Récupère l'application en cours d'exécution.
        print("4")
        pseudo = app.pseudo_c.text  # Récupère le pseudonyme de l'utilisateur.
        print("5")
        msg = "ajouter:" + self.user + ":" + pseudo  # Prépare le message d'ajout.
        print("6")
        if self.user not in self.user_accept:  # Vérifie si l'utilisateur n'est pas déjà accepté.
            app.client_handler.send_message(msg)  # Envoie le message d'ajout au serveur.
            print("7")
        else:
            print("8")
            # Affiche une notification si l'utilisateur a déjà été accepté.
            notification.notify(
                title="Demande de discussion",
                message="déjà accepté",  # Message de notification.
                app_name='My Application',
                app_icon=None,  # Optionnel : chemin vers une icône.
                timeout=50  # Durée avant la disparition de la notification.
            )

    def verification(self):
        # Démarre un processus de vérification des messages entrants.
        app = MDApp.get_running_app()  # Récupère l'application en cours d'exécution.

        def check_for_messages(dt):
            # Vérifie si des messages sont reçus.
            if app.client_handler:
                msg = app.client_handler.reponse  # Récupère la réponse du client.
                if msg:
                    Clock.schedule_once(lambda dt: self.notification(msg))  # Traite le message si reçu.
                    app.client_handler.reponse = None  # Réinitialise la réponse.

        def verification_thread():
            # Démarre une vérification régulière des messages.
            Clock.schedule_interval(check_for_messages, 1)  # Vérifie toutes les secondes.

        # Démarre le thread pour la vérification des messages.
        threading.Thread(target=verification_thread, daemon=True).start()

    def notification(self, msg):
        # Traite les notifications basées sur les messages reçus.
        app = MDApp.get_running_app()  # Récupère l'application en cours d'exécution.
        parts = msg.split(':')  # Sépare le message en parties.
        command, content = parts[0], parts[1]  # Récupère la commande et le contenu.

        if command.strip() == "accepté":  # Vérifie si la commande est "accepté".
            if content not in self.user_accept:  # Si l'utilisateur n'est pas déjà accepté.
                self.user_accept.append(content)  # L'ajoute à la liste des utilisateurs acceptés.
            aes_key = app.crypter.generate_aes_key()  # Génère une clé AES.
            pub = self.dic_u_pub[content]  # Récupère la clé publique de l'utilisateur.
            en_aes = app.crypter.encrypt_aes_key(pub, aes_key)  # Chiffre la clé AES avec la clé publique.
            en_aes_b64 = (base64.b64encode(en_aes).decode('utf-8'))  # Encode la clé chiffrée en base64.
            msg_r = "repons:" + content + ":" + en_aes_b64 + ":" + app.pseudo_c.text  # Prépare la réponse.
            app.client_handler.send_message(msg_r)  # Envoie la réponse au serveur.
            if content not in app.aes_cli.keys():  # Vérifie si la clé AES n'est pas déjà stockée.
                app.aes_cli[content] = aes_key  # Stocke la clé AES pour cet utilisateur.

        else:
            pass  # Ne fait rien si la commande n'est pas "accepté".

        # Affiche une notification pour confirmer l'état de la discussion.
        notification.notify(
            title="confirmation de discussion",
            message=content + " a " + command,  # Message de notification indiquant l'état de la discussion.
            app_name='My Application',
            app_icon=None,  # Optionnel : chemin vers une icône.
            timeout=50  # Durée avant la disparition de la notification.
        )

