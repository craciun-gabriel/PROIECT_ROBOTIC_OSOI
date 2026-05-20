from coppeliasim_zmqremoteapi_client import RemoteAPIClient

def connect_to_simulator():
    """
    Stabilește conexiunea cu serverul ZMQ al CoppeliaSim.
    Returnează clientul și obiectul principal 'sim' pentru apelarea API-ului.
    """
    try:
        client = RemoteAPIClient()
        sim = client.require('sim')
        return client, sim
    except Exception as e:
        print(f"Eroare la conectare: {e}")
        print("Asigură-te că simulatorul CoppeliaSim este deschis și rulează!")
        return None, None