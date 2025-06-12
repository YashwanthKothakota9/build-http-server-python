[![progress-banner](https://backend.codecrafters.io/progress/http-server/35633b1d-9461-4048-b571-2fdacaf174e8)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

This is a starting point for Python solutions to the
["Build Your Own HTTP server" Challenge](https://app.codecrafters.io/courses/http-server/overview).

[HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) is the
protocol that powers the web. In this challenge, you'll build a HTTP/1.1 server
that is capable of serving multiple clients.

Along the way you'll learn about TCP servers,
[HTTP request syntax](https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html),
and more.

**Note**: If you're viewing this repo on GitHub, head over to
[codecrafters.io](https://codecrafters.io) to try the challenge.


```
This implementation of HTTP server from scratch uses TCP primitives instead of using Python's built-in HTTP libraries 
```



### Stage 1: Bind server to a port
- Create a server using `socket` module
- bind it to a port `4221`
- wait for incoming client connections using `accept()`

### Stage 2: HTTP Response to the connection
- Server should respond to the accepted connection with `200` http response.

### Stage 3: URL Path parsing from request
- Server should send response based on the URL path in the HTTP request.
- HTTP `200` response for `GET \` request
- HTTP `404` response for anything other than above url path.

### Stage 4: Response with body
- Server should reponse with body
- HTTP `200` response for `GET \echo\{str}` request with response body of `{str}`

### Stage 5: Read header 
- Server should response with body the value of `User-agent` from headers
- HTTP `200` response for `GET \user-agent` request with response body with `User-agent`s value from headers. 