import time
from collections import deque
from typing import List ,Callable,Any

class APIKeyManager:
  
    def __init__(self, api_keys: List[str], requests_per_window: int, window_in_minutes: int):
        
        if not api_keys:
            raise ValueError("La liste des clés API ne peut pas être vide.")

        self.keys = deque(api_keys)
        
        self.max_requests = requests_per_window
        self.window_seconds = window_in_minutes * 60
        self.usage = {key: deque() for key in api_keys}

    def get_available_key(self) -> str:
        """
        Récupère une clé API valide qui n'a pas atteint sa limite de taux.
        
        Si toutes les clés ont atteint leur limite, cette méthode attendra
        qu'une clé redevienne disponible avant de la retourner.
        
        :return: Une clé API disponible.
        """
        # On essaie chaque clé une fois dans le cycle actuel
        for _ in range(len(self.keys)):
            key = self.keys.popleft() 
            current_time = time.time()
            
            timestamps = self.usage[key]
            
          
            while timestamps and timestamps[0] < current_time - self.window_seconds:
                timestamps.popleft()
                
            if len(timestamps) < self.max_requests:
                timestamps.append(current_time)  # Enregistrer l'utilisation actuelle
                self.keys.append(key)             # Remettre la clé à la fin de la file pour la prochaine rotation
                return key                        # Retourner la clé
            else:
               
                self.keys.append(key)
        
        print("Toutes les clés API ont atteint leur limite de taux. Mise en attente...")
        
        oldest_request_time = float('inf')
        for key in self.keys:
            if self.usage[key]:
                oldest_request_time = min(oldest_request_time, self.usage[key][0])
        
        wait_time = (oldest_request_time + self.window_seconds) - time.time() + 1
        
        if wait_time > 0:
            print(f"Attente de {wait_time:.2f} secondes...")
            time.sleep(wait_time)
            
        return self.get_available_key()



def with_api_key(manager: 'APIKeyManager') -> Callable:
    """
    Fabrique de décorateurs qui injecte une clé API dans une fonction.
    La fonction décorée DOIT accepter un argument nommé 'api_key'.
    """
    def decorator(func: Callable) -> Callable: 
        def wrapper_function(*args, **kwargs) -> Any:
            """
            La fonction 'wrapper' qui sera exécutée à la place de la fonction d'origine.
            """
            available_key = manager.get_available_key()
            kwargs['api_key'] = available_key

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                print(f"Erreur lors de l'appel API avec la clé {available_key[:12]}...: {e}")
                raise  

        return wrapper_function
    return decorator