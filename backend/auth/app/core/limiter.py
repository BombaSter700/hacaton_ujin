from slowapi import Limiter
from slowapi.util import get_remote_address

# Trust forwarded client addresses only after configuring a trusted reverse proxy.
limiter = Limiter(key_func=get_remote_address)
