import socket  # noqa: F401


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    clinet_socket, addr = server_socket.accept()  # wait for client
    with clinet_socket as conn:
        data = conn.recv(1024)
        request = data.decode("utf-8")
        request_path = request.split(" ")[1]

        if request_path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif request_path.startswith("/echo"):
            random_input_string = request_path[6:]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(random_input_string)}\r\n\r\n{random_input_string}\r\n"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        conn.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    main()
