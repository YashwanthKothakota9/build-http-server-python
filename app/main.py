import socket
import sys
from concurrent.futures import ThreadPoolExecutor


def response_with_body(body: str, file=False):
    if file:
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}\r\n\r\n"
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{body}\r\n\r\n"


def data_parser(data: bytes):
    data = data.decode("utf-8")
    request_lines = data.split("\r\n")
    return request_lines


def handle_client(client_socket: socket.socket, dir_name: str = None):
    with client_socket as conn:
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
        elif request_path.startswith("/files"):
            request_method = request_lines[0].split(" ")[0]
            file_name = request_path[7:]
            if request_method == "GET":
                try:
                    with open(f"{dir_name}/{file_name}", "r") as file:
                        response = response_with_body(file.read(), True)
                except FileNotFoundError:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
            elif request_method == "POST":
                request_body = request_lines[-1]
                with open(f"{dir_name}/{file_name}", "w") as file:
                    file.write(request_body)
                response = "HTTP/1.1 201 Created\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        conn.sendall(response.encode("utf-8"))


def main():
    dir_name = None
    n = len(sys.argv)
    if n > 1:
        dir_name = sys.argv[2]
        print(f"dir_name: {dir_name}")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    with ThreadPoolExecutor(max_workers=10)as executor:
        while True:
            clinet_socket, addr = server_socket.accept()
            executor.submit(handle_client, clinet_socket, dir_name)


if __name__ == "__main__":
    main()
