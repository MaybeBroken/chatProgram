import ngrok
from time import sleep


forward = ngrok.forward(
    8765, authtoken=input("authToken: ")
)

print(f"running server at URL {forward.url()}")
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("Exit")
