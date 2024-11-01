import hmac
import hashlib
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class MessageSecurity:
    def __init__(self):
        """Initialise les attributs pour la gestion des clés et du chiffrement."""
        self.__private_key = None  # Clé privée RSA
        self._public_key = None     # Clé publique RSA
        self.__aes_key = None       # Clé AES pour le chiffrement symétrique
        self._encrypted_aes_key = None  # Clé AES chiffrée
        self._iv = None             # Vecteur d'initialisation pour AES

    def generate_rsa_keys(self, bits=3072):
        """Génère une paire de clés RSA (publique et privée)."""
        try:
            key = RSA.generate(bits)  # Génération d'une nouvelle paire de clés RSA
            self.private_key = key.export_key()  # Exportation de la clé privée
            self.public_key = key.publickey().export_key()  # Exportation de la clé publique
        except Exception as e:
            raise RuntimeError("Erreur lors de la génération des clés RSA: " + str(e))

    def generate_aes_key(self):
        """Génère une clé AES de 256 bits (32 octets)."""
        try:
            self.aes_key = get_random_bytes(32)  # 256 bits pour AES
            return self.aes_key
        except Exception as e:
            raise RuntimeError("Erreur lors de la génération de la clé AES: " + str(e))

    def encrypt_aes_key(self, pub, aes_key):
        """Chiffre la clé AES avec la clé publique RSA."""
        self.public_key = pub  # Stockage de la clé publique
        self.aes_key = aes_key  # Stockage de la clé AES
        if self.public_key is None or self.aes_key is None:
            raise ValueError("Clé publique ou clé AES non définie.")
        try:
            rsa_key = RSA.import_key(self.public_key)  # Importation de la clé publique
            cipher_rsa = PKCS1_OAEP.new(rsa_key)  # Création de l'objet de chiffrement RSA
            self.encrypted_aes_key = cipher_rsa.encrypt(self.aes_key)  # Chiffrement de la clé AES
            return self.encrypted_aes_key
        except Exception as e:
            raise RuntimeError("Erreur lors du chiffrement de la clé AES: " + str(e))

    def decrypt_aes_key(self, pri, aes_key):
        """Déchiffre la clé AES avec la clé privée RSA."""
        self.private_key = pri  # Stockage de la clé privée
        self.encrypted_aes_key = aes_key  # Stockage de la clé AES chiffrée
        if self.private_key is None or self.encrypted_aes_key is None:
            raise ValueError("Clé privée ou clé AES chiffrée non définie.")
        try:
            rsa_key = RSA.import_key(self.private_key)  # Importation de la clé privée
            cipher_rsa = PKCS1_OAEP.new(rsa_key)  # Création de l'objet de déchiffrement RSA
            return cipher_rsa.decrypt(self.encrypted_aes_key)  # Déchiffrement de la clé AES
        except Exception as e:
            raise RuntimeError("Erreur lors du déchiffrement de la clé AES: " + str(e))

    def encrypt_message(self, message, aes_key):
        """Chiffre un message avec la clé AES et génère un HMAC."""
        self.aes_key = aes_key  # Stockage de la clé AES
        if self.aes_key is None:
            raise ValueError("Clé AES non définie.")
        try:
            self.iv = get_random_bytes(16)  # Génération du vecteur d'initialisation
            cipher_aes = AES.new(self.aes_key, AES.MODE_CBC, self.iv)  # Création de l'objet de chiffrement AES
            ciphertext = cipher_aes.encrypt(pad(message.encode(), AES.block_size))  # Chiffrement du message
            hmac_value = hmac.new(self.aes_key, ciphertext, hashlib.sha256).digest()  # HMAC du message chiffré
            return ciphertext, hmac_value, self.iv  # Retourne le message chiffré, le HMAC et le IV
        except Exception as e:
            raise RuntimeError("Erreur lors du chiffrement du message: " + str(e))

    def decrypt_message(self, ciphertext, hmac_value, aes_key, iv):
        """Déchiffre un message et vérifie son authenticité à l'aide du HMAC."""
        self.iv = iv  # Stockage du vecteur d'initialisation
        if aes_key is None or self.iv is None:
            raise ValueError("Clé AES ou vecteur d'initialisation non définis.")
        try:
            # Calcul de l'HMAC pour vérifier l'intégrité du message
            hmac_computed = hmac.new(self.aes_key, ciphertext, hashlib.sha256).digest()

            # Comparaison de l'HMAC calculé avec l'HMAC fourni
            if not hmac.compare_digest(hmac_computed, hmac_value):
                raise ValueError("Authenticité du message non vérifiée.")

            # Déchiffrement du message
            cipher_aes = AES.new(self.aes_key, AES.MODE_CBC, self.iv)
            decrypted_message = unpad(cipher_aes.decrypt(ciphertext), AES.block_size).decode()  # Message déchiffré
            return decrypted_message
        except Exception as e:
            raise RuntimeError("Erreur lors du déchiffrement du message: " + str(e))

    # Getters et Setters
    @property
    def private_key(self):
        """Getter pour la clé privée."""
        return self.__private_key

    @private_key.setter
    def private_key(self, value):
        """Setter pour la clé privée."""
        self.__private_key = value

    @property
    def public_key(self):
        """Getter pour la clé publique."""
        return self._public_key

    @public_key.setter
    def public_key(self, value):
        """Setter pour la clé publique."""
        self._public_key = value

    @property
    def aes_key(self):
        """Getter pour la clé AES."""
        return self.__aes_key

    @aes_key.setter
    def aes_key(self, value):
        """Setter pour la clé AES."""
        self.__aes_key = value

    @property
    def encrypted_aes_key(self):
        """Getter pour la clé AES chiffrée."""
        return self._encrypted_aes_key

    @encrypted_aes_key.setter
    def encrypted_aes_key(self, value):
        """Setter pour la clé AES chiffrée."""
        self._encrypted_aes_key = value

    @property
    def iv(self):
        """Getter pour le vecteur d'initialisation."""
        return self._iv

    @iv.setter
    def iv(self, value):
        """Setter pour le vecteur d'initialisation."""
        self._iv = value
