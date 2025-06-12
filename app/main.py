import socket  # noqa: F401


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, addr = server_socket.accept()  # wait for client
    if conn.recv(1024) == b"GET / HTTP/1.1\r\nHost: localhost:4221\r\n\r\n":
        conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
    else:
        conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
