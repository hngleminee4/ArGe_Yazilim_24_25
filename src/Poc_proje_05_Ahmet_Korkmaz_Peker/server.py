import socket
import cv2

def main():
    server_ip = "0.0.0.0"
    server_port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)
    print(f"Sunucu başlatıldı: {server_ip}:{server_port}")
    conn, addr = server_socket.accept()
    print(f"Bağlantı kabul edildi: {addr}")

    cap = cv2.VideoCapture(0)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()
            size = f"{len(data):<16}".encode('utf-8')
            conn.sendall(size + data)
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        cap.release()
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    main()
