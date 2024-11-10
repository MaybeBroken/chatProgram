import ngrok
from time import sleep


forward = ngrok.forward(
    8765, authtoken="2hQokC8qEf1kJ4KV1j0pdTLwJA1_F5A9uFbRGuWfaq6xza1A"
)

print(f"running server at URL {forward.url()}")
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("Exit")
