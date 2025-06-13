import socket
import sys
import gzip
from concurrent.futures import ThreadPoolExecutor


def compress_data(data: str):
    return gzip.compress(data.encode("utf-8"))


def response_with_body(body: str, file=False, close=False):
    if file:
        if close:
            return f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nConnection: close\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    if close:
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{body}"


def response_with_encoding(compressed_data, close=False):
    if close:
        header = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\nContent-Encoding: gzip\r\nContent-Length: {len(compressed_data)}\r\n\r\n"
        return header.encode("utf-8") + compressed_data
    header = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Encoding: gzip\r\nContent-Length: {len(compressed_data)}\r\n\r\n"
    return header.encode("utf-8") + compressed_data


def response_with_close():
    return "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"


def parse_http_request(data: bytes):
    """Parse HTTP request and return request path and headers"""
    data = data.decode("utf-8")
    request_lines = data.split("\r\n")
    request_line = request_lines[0]
    method, path, version = request_line.split(" ")

    # Parse headers into a dictionary
    headers = {}
    for line in request_lines[1:]:
        if not line:  # Empty line marks end of headers
            break
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

    return method, path, headers, ""


def handle_client(client_socket: socket.socket, dir_name: str = None):
    buffer = b""
    while True:
        try:
            # Receive data from client
            data = client_socket.recv(1024)
            if not data:  # Client closed connection
                break

            buffer += data

            # Process complete requests
            while b"\r\n\r\n" in buffer:
                # Split request and remaining data
                request, buffer = buffer.split(b"\r\n\r\n", 1)
                request += b"\r\n\r\n"  # Add back the separator

                # Parse the request
                method, request_path, headers, _ = parse_http_request(request)

                # Get body if Content-Length is present
                body = ""
                if "Content-Length" in headers:
                    content_length = int(headers["Content-Length"])
                    if len(buffer) >= content_length:
                        body = buffer[:content_length].decode("utf-8")
                        buffer = buffer[content_length:]

                # print(f"method: {method}")
                # print(f"request_path: {request_path}")
                # print(f"headers: {headers}")
                # print(f"body: {body}")

                # Handle the request
                if request_path == "/":
                    if "Connection" in headers and headers["Connection"] == "close":
                        response = response_with_close()
                        client_socket.sendall(response.encode("utf-8"))
                        client_socket.close()
                        return
                    else:
                        response = "HTTP/1.1 200 OK\r\n\r\n"
                elif request_path == "/user-agent":
                    user_agent = headers.get("User-Agent", "")
                    if "Connection" in headers and headers["Connection"] == "close":
                        response = response_with_body(user_agent, close=True)
                        client_socket.sendall(response.encode("utf-8"))
                        client_socket.close()
                        return
                    else:
                        response = response_with_body(user_agent)
                elif request_path.startswith("/echo"):
                    if "Accept-Encoding" in headers:
                        compression_methods = headers["Accept-Encoding"].split(
                            ",")
                        compression_methods = [method.strip()
                                               for method in compression_methods]
                        if "gzip" in compression_methods:
                            compressed_data = compress_data(request_path[6:])
                            if "Connection" in headers and headers["Connection"] == "close":
                                response = response_with_encoding(
                                    compressed_data, close=True)
                                client_socket.sendall(response)
                                client_socket.close()
                                return
                            response = response_with_encoding(compressed_data)
                            client_socket.sendall(response)
                            continue
                    random_input_string = request_path[6:]
                    if "Connection" in headers and headers["Connection"] == "close":
                        response = response_with_body(
                            random_input_string, close=True)
                        client_socket.sendall(response.encode("utf-8"))
                        client_socket.close()
                        return
                    else:
                        response = response_with_body(random_input_string)
                elif request_path.startswith("/files"):
                    file_name = request_path[7:]
                    if method == "GET":
                        try:
                            with open(f"{dir_name}/{file_name}", "r") as file:
                                if "Connection" in headers and headers["Connection"] == "close":
                                    response = response_with_body(
                                        file.read(), True, close=True)
                                    client_socket.sendall(
                                        response.encode("utf-8"))
                                    client_socket.close()
                                    return
                                else:
                                    response = response_with_body(
                                        file.read(), True)
                        except FileNotFoundError:
                            response = "HTTP/1.1 404 Not Found\r\n\r\n"
                    elif method == "POST":
                        try:
                            with open(f"{dir_name}/{file_name}", "w") as file:
                                file.write(body)
                            if "Connection" in headers and headers["Connection"] == "close":
                                response = "HTTP/1.1 201 Created\r\nConnection: close\r\n\r\n"
                                client_socket.sendall(response.encode("utf-8"))
                                client_socket.close()
                                return
                            else:
                                response = "HTTP/1.1 201 Created\r\n\r\n"
                        except Exception as e:
                            print(f"Error writing file: {e}")
                            response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                else:
                    if "Connection" in headers and headers["Connection"] == "close":
                        response = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"
                        client_socket.sendall(response.encode("utf-8"))
                        client_socket.close()
                        return
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"

                # Send response
                client_socket.sendall(response.encode("utf-8"))

        except (socket.error, ConnectionResetError) as e:
            print(f"Connection error: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    client_socket.close()


def main():
    dir_name = None
    n = len(sys.argv)
    if n > 1:
        dir_name = sys.argv[2]
        # print(f"dir_name: {dir_name}")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            client_socket, addr = server_socket.accept()
            executor.submit(handle_client, client_socket, dir_name)


if __name__ == "__main__":
    main()
