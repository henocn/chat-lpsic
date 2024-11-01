from kivymd.uix.tab import MDTabsBase  # Importer MDTabsBase pour la fonctionnalité des onglets
from kivymd.uix.card import MDCard  # Importer MDCard pour les éléments d'interface utilisateur basés sur des cartes
from kivymd.uix.floatlayout import MDFloatLayout  # Importer MDFloatLayout pour une mise en page flexible
from kivy.properties import ListProperty  # Importer ListProperty pour les propriétés de couleur
from kivy.uix.relativelayout import RelativeLayout  # Importer RelativeLayout pour le positionnement relatif
from kivymd.uix.label import MDLabel  # Importer MDLabel pour les éléments d'interface utilisateur étiquetés
from kivymd.uix.behaviors.hover_behavior import HoverBehavior  # Importer HoverBehavior pour les effets de survol
from kivy.properties import StringProperty, NumericProperty  # Importer des propriétés pour les éléments d'interface utilisateur dynamiques
from kivymd.uix.dialog import MDDialog  # Importer MDDialog pour les boîtes de dialogue
from kivymd.uix.button import MDFlatButton  # Importer MDFlatButton pour les éléments d'interface utilisateur de type bouton plat


class MyHoverCard(MDCard, HoverBehavior):
    """
    Carte personnalisée qui change de couleur lorsqu'elle est survolée.
    Hérite de MDCard et implémente HoverBehavior.
    """
    default_color = ListProperty([0.9, 0.95, 1, 1])  # Couleur par défaut (bleu clair)
    hover_color = ListProperty([0.8, 0.9, 1, 1])  # Couleur au survol (rouge clair)

    def on_enter(self, *args):
        """Appelé lorsque le curseur de la souris entre dans la zone de la carte."""
        self.md_bg_color = self.hover_color  # Changer la couleur de fond en hover_color

    def on_leave(self, *args):
        """Appelé lorsque le curseur de la souris quitte la zone de la carte."""
        self.md_bg_color = self.default_color  # Changer la couleur de fond en default_color


class Tab(MDFloatLayout, MDTabsBase):
    """
    Classe implémentant le contenu d'un onglet.
    Hérite de MDFloatLayout et MDTabsBase pour prendre en charge les onglets.
    """


class Command(MDLabel):
    """
    Classe pour les étiquettes de commande avec des propriétés supplémentaires.
    Hérite de MDLabel.
    """
    text = StringProperty()  # Propriété de texte pour l'étiquette
    size_hint_x = NumericProperty()  # Indice de taille horizontal pour l'étiquette
    halign = StringProperty()  # Alignement horizontal du texte
    font_size = 17  # Taille de police du texte


class Response(MDLabel):
    """
    Classe pour les étiquettes de réponse avec des propriétés supplémentaires.
    Hérite de MDLabel.
    """
    text = StringProperty()  # Propriété de texte pour l'étiquette
    size_hint_x = NumericProperty()  # Indice de taille horizontal pour l'étiquette
    halign = StringProperty()  # Alignement horizontal du texte
    font_size = 17  # Taille de police du texte


class ClickableTextFieldRound(RelativeLayout):
    """
    Champ de texte personnalisé avec des indices cliquables.
    Hérite de RelativeLayout pour un positionnement flexible.
    """
    text = StringProperty()  # Propriété de texte pour le champ de texte
    hint_text = StringProperty()  # Texte d'indice pour le champ de texte

    def show_info(self):
        """Affiche une boîte de dialogue d'information en fonction du texte d'indice."""
        # Déterminer le message en fonction du texte d'indice
        if self.hint_text == "Pseudo_s":
            msg = "Identifiant du serveur"  # Identifiant du serveur
        elif self.hint_text == "Description_s":
            msg = "La description de votre serveur"  # Description du serveur
        elif self.hint_text == "max_client":
            msg = "Le nombre maximal de connexions au serveur"  # Nombre maximal de clients autorisés
        elif self.hint_text == "Port":
            msg = "Un port du serveur"  # Port du serveur
        elif self.hint_text == "Pseudo_c":
            msg = "Votre identifiant dans le réseau"  # Votre identifiant dans le réseau
        elif self.hint_text == "Description_c":
            msg = "Comment vous reconnaître ?"  # Comment vous reconnaître ?
        elif self.hint_text == "SERVER_IP":
            msg = "L'adresse IP du serveur"  # Adresse IP du serveur
        elif self.hint_text == "SERVER_PORT":
            msg = "Le port du serveur"  # Port du serveur

        # Créer une boîte de dialogue pour afficher le message
        dialog = MDDialog(
            text=msg,  # Définir le texte de la boîte de dialogue
            size_hint=(0.8, 0.2),  # Définir la taille de la boîte de dialogue
            buttons=[  # Définir les boutons de la boîte de dialogue
                MDFlatButton(
                    text="OK",  # Texte du bouton
                    on_release=lambda x: dialog.dismiss()  # Fermer la boîte de dialogue lorsque pressé
                )
            ]
        )
        dialog.open()  # Ouvrir la boîte de dialogue
