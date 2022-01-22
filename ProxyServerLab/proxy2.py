#Author: Nick Onofrei

from socket import *
import sys

# Create a server socket
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# Bind host name and port to server socket
tcpSerSock.bind((sys.argv[1], 8888))
# Start listening
tcpSerSock.listen(1)
# Fill in end.

while 1:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    # Fill in start.
    message = tcpCliSock.recv(1024)  # (1) Receive message from client
    # Fill in end.
    # Decode message (bytes object) into str
    message_to_string = message.decode()
    print(message_to_string)
    # Extract the filename from the given message
    filename = message_to_string.split()[1].partition("/")[2]
    print("filename: " + filename)
    fileExist = "false"
    filetouse = "/" + filename
    print("filetouse: " + filetouse)

    try:
        # Check whether the file exist in the cache
        f = open(filetouse[1:], "rb")
        outputdata = f.readlines()

        fileExist = "true"
        # ProxyServer finds a cache hit and generates a response message
        response_header = "HTTP/1.0 200 OK\r\n"
        entity_header = "Content-Type:text/html\r\n"
        tcpCliSock.send(response_header.encode())
        tcpCliSock.send(entity_header.encode())

        # Creates the response message
        response = ""
        for string in outputdata:
            response += string.decode()

        tcpCliSock.send(response.encode())

        print('Read from cache')
    # Error handling for file not found in cache
    except IOError:
        if fileExist == "false":
            # Create a socket on the proxy server to the web server
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace("www.", "", 1)
            print(hostn)
            try:
                # Set an appropriate timeout for the web server socket
                c.settimeout(1000)
                # Connect the web server socket to port 80
                c.connect((hostn, 80))

                # Send client's GET request to web server
                get_request = "GET " + '/' + " HTTP/1.0\r\n\r\n"
                # get_request = "GET / HTTP/1.1\r\nHost: " + filename + "\r\n\r\n" #--> This should also work
                c.send(get_request.encode())

                # Create a file to cache the response from the web server
                tmpFile = open("./" + filename, "wb")

                # Keep on receiving parts of the webpage until there is no more data
                response = c.recv(4096).decode()
                while True:
                    try:
                        response += c.recv(4096).decode()
                    except:
                        #print("Failed To Get HTTP Page\n")
                        break
                response = response.encode()

                # Write to file
                tmpFile.write(response)
                tmpFile.close()

                if (filename[-1:] == '/'):
                    filename = filename[:-1]
                # Send response
                tcpCliSock.send(response)
                c.close()

            except:
                print("Illegal request")
        else:
            # Send an HTTP response message for file not found to the client
            tcpCliSock.send("HTTP/1.0 404 SendError\r\n")
            tcpCliSock.send("Content-Type:text/html\r\n")
            tcpCliSock.send("\r\n")

    # Close the client socket
    tcpCliSock.close()
