from requests import get

def neko():
    return get('http://kuchizu.herokuapp.com/').json()
