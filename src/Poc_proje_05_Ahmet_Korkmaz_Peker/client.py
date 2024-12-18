import socket
import cv2
import numpy as np

def main():
    server_ip = "10.0.0.169"  # Jetson'un IP adresini girin
    server_port = 5000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    print(f"Sunucuya bağlanıldı: {server_ip}:{server_port}")

    data = b""
    payload_size = 16
    try:
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    break
                data += packet
            msg_size = int(data[:payload_size].decode('utf-8'))
            data = data[payload_size:]

            while len(data) < msg_size:
                data += client_socket.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow("PC Görüntü", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        client_socket.close()
        cv2.destroyAllWindows()
main()