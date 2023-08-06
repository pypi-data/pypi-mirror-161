__all__ = ["VialLoginManager"]

import os
import time
import json
import uuid
import hashlib

from pathlib import Path

class VialLoginManager():
    """
    A simple login/session manager
    """
    def __init__(self, session_dir="sessions", ttl=3600):
        self.session_dir = session_dir
        self.ttl = ttl
        if not os.path.isdir(session_dir):
            os.makedirs(session_dir)

    def __getitem__(self, session_id):
        spath = os.path.join(self.session_dir, session_id)
        if not os.path.exists(spath):
            return None
        if os.path.getmtime(spath) < time.time() - self.ttl:
            del(self[session_id])
        else:
            Path(spath).touch()
        try:
            return json.load(open(spath))
        except Exception:
            del(self[session_id])
            return None

    def __setitem__(self, session_id, data):
        for f in os.listdir(self.session_dir):
            spath = os.path.join(self.session_dir, f)
            if os.path.getmtime(spath) < time.time() - self.ttl:
                del(self[f])
        spath = os.path.join(self.session_dir, session_id)
        with open(spath, "w") as sf:
            json.dump(data, sf)

    def __delitem__(self, session_id):
        spath = os.path.join(self.session_dir, session_id)
        try:
            os.remove(spath)
        except Exception:
            pass

    def authorize(self, login:str, password:str):
        """
        Reimplement this method to use your authetication backend.
        Return value must be a JSON serializable object with the user data.
        """
        return {"login" : login, "full_name" : "Anonymous"}

    def create_session(self, data):
        string = str(uuid.uuid1()).encode("ascii")
        session_id =  hashlib.sha256(string).hexdigest()
        self[session_id] = data
        return session_id

    def login(self, **kwargs):
        login = kwargs.get("login")
        password = kwargs.get("password")
        if not (login and password):
            return None
        user = self.authorize(login, password)
        return self.create_session(user) if user else None

    def logout(self, session_id):
        del(self[session_id])

