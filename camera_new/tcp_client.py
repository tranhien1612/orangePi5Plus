import socket

def start_tcp_client(host='127.0.0.1', port=10001):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Connect to the server
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        
        while True:
            hex_input = input("Enter hex data to send (e.g., '010203'): ")
            try:
                raw_data = bytes.fromhex(hex_input)
            except ValueError:
                print("Invalid hex input. Please enter a valid hex string.")
                continue
            
            # Send the raw binary data to the server
            client_socket.sendall(raw_data)

if __name__ == "__main__":
    start_tcp_client()