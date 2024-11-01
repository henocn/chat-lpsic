import sqlite3

class DatabaseManager:
    def __init__(self, db_name='chatLPSIC.db'):
        """Initialise le gestionnaire de base de données avec un nom de base de données par défaut."""
        self.db_name = db_name  # Nom de la base de données
        self.conn = None  # Connexion à la base de données
        self.cursor = None  # Curseur pour exécuter des requêtes

    def connect(self):
        """Établit une connexion à la base de données et retourne l'objet de connexion."""
        try:
            self.conn = sqlite3.connect(self.db_name)  # Connexion à la base de données
            self.cursor = self.conn.cursor()  # Création d'un curseur
            return self.conn  # Retourne l'objet de connexion
        except sqlite3.Error as e:
            print(f"Erreur de connexion à la base de données : {e}")  # Affiche une erreur en cas d'échec
            return None  # Retourne None si la connexion échoue

    def create_table(self):
        """Crée la table 'messages' si elle n'existe pas déjà."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique pour chaque message
                sender VARCHAR(10) NOT NULL,           -- Expéditeur du message
                receiver VARCHAR(10) NOT NULL,         -- Destinataire du message
                statut VARCHAR(10) NOT NULL,           -- Statut du message (ex: lu, non lu)
                message TEXT NOT NULL,                 -- Contenu du message
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  -- Horodatage du message
            )
        ''')

    def store_message(self, sender, receiver, statut, message):
        """Stocke un message dans la base de données."""
        conn = self.connect()  # Établit la connexion à la base de données
        if conn is None:
            return  # Retourne si la connexion échoue
        try:
            query = '''
                INSERT INTO messages (sender, receiver, statut, message)
                VALUES (?, ?, ?, ?)
            '''  # Requête pour insérer un message
            self.cursor.execute(query, (sender, receiver, statut, message))  # Exécute la requête d'insertion
            conn.commit()  # Valide les changements dans la base de données
        except sqlite3.Error as e:
            print(f"Erreur lors de l'insertion du message : {e}")  # Affiche une erreur en cas d'échec d'insertion
        finally:
            conn.close()  # Ferme la connexion à la base de données

    def get_messages(self, query, x):
        """Récupère les messages de la base de données selon une requête spécifiée."""
        conn = self.connect()  # Établit la connexion à la base de données
        if conn is None:
            return []  # Retourne une liste vide si la connexion échoue
        try:
            self.cursor.execute(query, x)  # Exécute la requête pour récupérer les messages
            return self.cursor.fetchall()  # Retourne tous les résultats de la requête
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des messages : {e}")  # Affiche une erreur en cas d'échec de récupération
            return []  # Retourne une liste vide en cas d'erreur
        finally:
            conn.close()  # Ferme la connexion à la base de données
