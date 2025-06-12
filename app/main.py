import socket


def response_with_body(body: str):
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{body}\r\n\r\n"


def data_parser(data: bytes):
    data = data.decode("utf-8")
    request_lines = data.split("\r\n")
    return request_lines


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    clinet_socket, addr = server_socket.accept()  # wait for client
    with clinet_socket as conn:
        data = conn.recv(1024)
        request_lines = data_parser(data)
        request_path = request_lines[0].split(" ")[1]

        if request_path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif request_path == "/user-agent":
            user_agent = request_lines[2].split()[-1]
            response = response_with_body(user_agent)
        elif request_path.startswith("/echo"):
            random_input_string = request_path[6:]
            response = response_with_body(random_input_string)
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        conn.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    main()
