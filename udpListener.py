import socket
from pymavlink import mavutil
import time
import threading

class MAVLinkUDPHandler:
    def __init__(self, host="127.0.0.1", port=14552):
        self.host = host
        self.port = port
        self.connected_clients = set()
        # Initialize MAVLink parser with appropriate dialect
        self.mav = mavutil.mavlink.MAVLink(None, srcSystem=1, srcComponent=1)
        self.running = True

    def decode_mavlink_message(self, data):
        """Decodes MAVLink message from raw data using proper parser."""
        try:
            msg = self.mav.parse_char(data)
            if msg is not None:
                print(f"Decoded MAVLink message: {msg}")
                print(f"Message Type: {msg.get_type()}")
                print(f"Message Content: {msg.to_dict()}")
                return msg
            return None
        except Exception as e:
            print(f"Failed to decode MAVLink message: {e}")
            return None

    

    def start(self):
        """Starts the UDP listener and message handler."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.port))
            print(f"MAVLink UDP Handler listening on {self.host}:{self.port}")

            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    
                    if addr not in self.connected_clients:
                        self.connected_clients.add(addr)
                        print(f"New client connected: {addr}")

                    print(f"Received message from {addr}: {data.hex()}")
                    
                    # Properly decode the message
                    decoded_msg = self.decode_mavlink_message(data)
                    if decoded_msg:
                        # Forward message to other clients
                        for client in self.connected_clients:
                            if client != addr:
                                sock.sendto(data, client)
                                
                except KeyboardInterrupt:
                    print("\nShutting down...")
                    self.running = False
                    break
                except Exception as e:
                    print(f"Error in message handling: {e}")

if __name__ == "__main__":
    handler = MAVLinkUDPHandler()
    handler.start()