import cv2
from ultralytics import YOLO

# Khởi tạo mô hình YOLO
model = YOLO("yolov8n.pt")  # Chọn mô hình YOLOv8, bạn có thể thay đổi thành mô hình YOLO khác nếu cần

# Mở camera (0 là camera mặc định)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Không thể mở camera")
    exit()

while True:
    # Đọc khung hình từ camera
    ret, frame = cap.read()
    if not ret:
        print("Không thể nhận khung hình từ camera")
        break

    # Chạy mô hình YOLO để phát hiện vật thể
    results = model(frame)

    # Kiểm tra và đánh dấu tất cả các vật thể được phát hiện
    detected_objects = []
    for result in results:
        for box in result.boxes:
            obj_name = result.names[int(box.cls)]  # Lấy tên của vật thể
            detected_objects.append(obj_name)

            # Vẽ khung chữ nhật cho vật thể
            x1, y1, x2, y2 = box.xyxy[0]  # Toạ độ bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)  # Vẽ bounding box
            cv2.putText(frame, obj_name, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # In ra các vật thể được phát hiện
    if detected_objects:
        print("Đã phát hiện:", ", ".join(set(detected_objects)))  # Sử dụng set để tránh lặp lại tên vật thể
    else:
        print("Không phát hiện vật thể nào.")

    # Hiển thị khung hình có chứa vật thể được phát hiện
    cv2.imshow("YOLO Object Detection", frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
