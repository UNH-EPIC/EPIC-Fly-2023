import socket

def main():
    server_host = '127.0.0.1'
    server_port = 8888

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_host, server_port))

    while True:
        message = input("Enter your message: ")
        client.send(message.encode())

        # Receive and display the response from the server
        response = client.recv(1024)
        print("Server response:", response.decode())

    client.close()

if __name__ == "__main__":
    main()
