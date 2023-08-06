from requests import get

class Kuchizu:
    def neko():
        return get('http://kuchizu.herokuapp.com/').json()
