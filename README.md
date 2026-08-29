# 🖱️ HumanCursor Py (`undetected-human-cursor`)

> **Thư viện giả lập tương tác trình duyệt (Mouse & Keyboard) chuẩn hành vi con người dành cho Python Selenium & Chrome CDP.**

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Selenium & UC](https://img.shields.io/badge/undetected--chromedriver-supported-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## 🌟 Tính Năng Nổi Bật (Features)

- **🛣️ Đường cong Bézier bậc 3 (Cubic Bézier Movement)**: Di chuyển con trỏ chuột theo đường cong tự nhiên thay vì đường thẳng cơ học.
- **⚡ Gia tốc & Giảm tốc (Ease-In-Out)**: Chuột tự động tăng tốc khi bắt đầu và giảm tốc mượt mà khi tiệm cận điểm đích.
- **🫨 Giả lập độ rung tay (Human Jitter & Drift)**: Thêm nhiễu tọa độ ngẫu nhiên dọc đường đi và chế độ nhúc nhích nhẹ khi tạm dừng (idle hover).
- **🎯 Click & Hover như người thật (Human Click & Hover)**:
  - Phản xạ dừng chuột ngẫu nhiên (50 - 120ms) trước khi click.
  - Đè giữ nút chuột (`mousePressed` -> `mouseReleased`) từ 40 - 100ms.
  - Tự động lệch nhẹ vị trí click ngẫu nhiên bên trong khung hiển thị phần tử (Element Bounding Box).
- **🖱️ Tương tác đa dạng**: Hỗ trợ Double Click, Context Click (chuột phải), Drag & Drop, và Scroll bằng con lăn.
- **⌨️ Đánh máy kiểu người (Human Typing)**: Gõ phím với tốc độ biến thiên, nhận diện dấu câu/khoảng trắng, tỷ lệ gõ nhầm phím lân cận và tự gõ `Backspace` để xóa sửa.
- **🔴 Virtual Cursor Overlay**: Hiển thị con trỏ màu đỏ ảo trực quan trên trang giúp dễ dàng quan sát/debug trong quá trình chạy automation.

---

## 📦 Yêu Cầu Hệ Thống (Requirements)

- Python 3.8+
- `undetected-chromedriver` hoặc `selenium`

```bash
pip install undetected-chromedriver
```

---

## 🚀 Hướng Dẫn Sử Dụng (Quick Start)

```python
import time
import undetected_chromedriver as uc
from main import HumanCursor  # Hoặc import từ module của bạn

# 1. Khởi tạo Chrome Driver
options = uc.ChromeOptions()
options.add_argument("--window-size=1200,700")
driver = uc.Chrome(options=options)

try:
    driver.get("https://example.com")
    time.sleep(2)

    # 2. Khởi tạo HumanCursor
    human = HumanCursor(driver, show_visual_cursor=True)

    # 3. Di chuyển chuột tới tọa độ (X, Y)
    human.move_to(500, 300)

    # 4. Rê chuột (Hover) & giữ nhúc nhích tay nhẹ trong 1.5 giây
    human.hover(400, 250, duration=1.5)

    # 5. Click chuột giống người
    human.click(500, 350)

    # 6. Click chuột phải (Context Click)
    human.context_click(600, 300)

    # 7. Cuộn trang bằng con lăn chuột
    human.scroll(delta_y=300)

    # 8. Kéo và thả (Drag & Drop)
    human.drag_and_drop(start_x=200, start_y=200, end_x=600, end_y=400)

    # 9. Tương tác trực tiếp với HTML Element (bằng CSS Selector)
    human.click_element("h1")

    # 10. Gõ phím như người (có giả lập gõ nhầm & xóa sửa)
    # human.type_like_human("Xin chào thế giới!", element_or_selector="input#search")

    time.sleep(3)

finally:
    driver.quit()
```

---

## 📖 Bảng Chi Tiết API (API Reference)

| Phương thức | Tham số | Mô tả |
| :--- | :--- | :--- |
| `move_to(target_x, target_y)` | `duration_factor=1.0, human_offset=True` | Di chuyển mượt theo quỹ đạo cong Bézier & độ rung tay |
| `hover(x, y, duration)` | `x, y, duration=None` | Rê chuột và duy trì nhúc nhích tay nhẹ tại vị trí |
| `click(x, y, button, clicks)` | `button="left", clicks=1` | Click chuột kiểu con người (có độ trễ đè nút) |
| `double_click(x, y)` | `x=None, y=None` | Nhấp đôi chuột kiểu con người |
| `context_click(x, y)` | `x=None, y=None` | Click chuột phải |
| `drag_and_drop(s_x, s_y, e_x, e_y)` | `start_x, start_y, end_x, end_y` | Kéo thả phần tử mượt mà |
| `scroll(delta_y, steps)` | `delta_y, steps=5` | Cuộn trang bằng con lăn chuột |
| `move_to_element(selector/el)` | `element_or_selector` | Di chuyển tới vị trí ngẫu nhiên trong khung của Element |
| `click_element(selector/el)` | `element_or_selector` | Di chuyển & click phần tử HTML |
| `hover_element(selector/el)` | `element_or_selector, duration` | Di chuyển & rê chuột trên phần tử HTML |
| `type_like_human(text, element)` | `text, element=None, error_rate=0.03` | Gõ phím giả lập tốc độ người gõ & tự sửa lỗi |

---

## 📄 License

Dự án phát hành dưới giấy phép **MIT License**. Bạn được tự do sử dụng, chỉnh sửa và thương mại hóa.
