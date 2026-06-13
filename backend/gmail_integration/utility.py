from cryptography.fernet import Fernet
from django.conf import settings

class TextSecurity:
    def __init__(self):
        self.key = settings.FERNET_KEY
        self.cipher = Fernet(self.key)

    def encrypt(self,text):
        # encode into utf-8
        text_bytes = text.encode('utf-8')
        # encrpyt 
        encrypted_text = self.cipher.encrypt(text_bytes)
        return encrypted_text.decode('utf-8')

    def decrypt(self, text):
        return self.cipher.decrypt(text.encode('utf-8'))
