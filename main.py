import math
import random
import time
import undetected_chromedriver as uc


class HumanCursor:
    """
    Class hỗ trợ di chuyển chuột và tương tác trình duyệt giả lập hành vi con người:
    - Quỹ đạo di chuyển cong Bézier tự nhiên.
    - Gia tốc và giảm tốc (Ease-In-Out).
    - Độ rung lắc tay (Human Jitter) & drift tự nhiên.
    - Human Click (có độ trễ phản xạ, thời gian đè chuột down/up).
    - Human Hover (rê chuột kết hợp nhúc nhích nhẹ).
    - Human Double Click, Context Click, Drag & Drop.
    - Human Scroll (cuộn trang mượt bằng con lăn).
    - Human Typing (gõ phím tốc độ biến thiên, tự động gõ nhầm và backspace sửa).
    """

    def __init__(self, driver, show_visual_cursor=True):
        self.driver = driver
        self.show_visual_cursor = show_visual_cursor
        self.current_pos = [0, 0]
        if self.show_visual_cursor:
            self.inject_visual_cursor()

    def inject_visual_cursor(self):
        """Tạo con trỏ giả lập màu đỏ hiển thị trên màn hình"""
        script = """
        (() => {
            if (document.getElementById("__virtual_cursor__")) return;
            const cursor = document.createElement("div");
            cursor.id = "__virtual_cursor__";
            Object.assign(cursor.style, {
                position: "fixed",
                width: "18px",
                height: "18px",
                border: "3px solid red",
                borderRadius: "50%",
                background: "rgba(255, 0, 0, 0.25)",
                pointerEvents: "none",
                zIndex: "2147483647",
                transform: "translate(-50%, -50%)",
                left: "0px",
                top: "0px",
                transition: "box-shadow 0.1s ease"
            });
            document.documentElement.appendChild(cursor);
        })();
        """
        try:
            self.driver.execute_script(script)
        except Exception:
            pass

    def _move_cursor_instant(self, x, y):
        """Cập nhật vị trí chuột tức thời trên DOM & gửi sự kiện CDP"""
        self.current_pos = [x, y]
        if self.show_visual_cursor:
            try:
                self.driver.execute_script("""
                    let cursor = document.getElementById("__virtual_cursor__");
                    if (cursor) {
                        cursor.style.left = arguments[0] + "px";
                        cursor.style.top = arguments[1] + "px";
                    } else {
                        cursor = document.createElement("div");
                        cursor.id = "__virtual_cursor__";
                        Object.assign(cursor.style, {
                            position: "fixed",
                            width: "18px",
                            height: "18px",
                            border: "3px solid red",
                            borderRadius: "50%",
                            background: "rgba(255, 0, 0, 0.25)",
                            pointerEvents: "none",
                            zIndex: "2147483647",
                            transform: "translate(-50%, -50%)",
                            left: arguments[0] + "px",
                            top: arguments[1] + "px",
                            transition: "box-shadow 0.1s ease"
                        });
                        document.documentElement.appendChild(cursor);
                    }
                """, x, y)
            except Exception:
                pass

        self.driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseMoved",
                "x": int(x),
                "y": int(y),
                "button": "none"
            }
        )

    def move_to(self, target_x, target_y, duration_factor=1.0, human_offset=True):
        """Di chuyển mượt mà tới tọa độ đích với đường cong Bezier & độ rung tay"""
        if human_offset:
            # Độ lệch nhẹ tự nhiên khi di chuyển đến điểm đích
            target_x += random.uniform(-2, 2)
            target_y += random.uniform(-2, 2)

        start_x, start_y = self.current_pos
        dist = math.hypot(target_x - start_x, target_y - start_y)
        if dist < 3:
            self._move_cursor_instant(target_x, target_y)
            return

        steps = max(20, int(dist / 10))

        # Độ cong đường đi ngẫu nhiên
        side = random.choice([-1, 1])
        curve_amount = random.uniform(15, min(70, dist * 0.35)) * side

        nx = -(target_y - start_y) / (dist + 1e-6)
        ny = (target_x - start_x) / (dist + 1e-6)

        p0 = (start_x, start_y)
        p1 = (start_x + (target_x - start_x) * 0.3 + nx * curve_amount,
              start_y + (target_y - start_y) * 0.3 + ny * curve_amount)
        p2 = (start_x + (target_x - start_x) * 0.7 + nx * curve_amount * 0.5,
              start_y + (target_y - start_y) * 0.7 + ny * curve_amount * 0.5)
        p3 = (target_x, target_y)

        for i in range(1, steps + 1):
            raw_t = i / steps
            # Ease-In-Out
            if raw_t < 0.5:
                t = 4 * raw_t * raw_t * raw_t
            else:
                t = 1 - math.pow(-2 * raw_t + 2, 3) / 2

            u = 1 - t
            x = (u**3 * p0[0] +
                 3 * u**2 * t * p1[0] +
                 3 * u * t**2 * p2[0] +
                 t**3 * p3[0])
            y = (u**3 * p0[1] +
                 3 * u**2 * t * p1[1] +
                 3 * u * t**2 * p2[1] +
                 t**3 * p3[1])

            # Rung tay nhẹ
            jitter_factor = (1 - raw_t) * 1.8
            jitter_x = random.uniform(-jitter_factor, jitter_factor)
            jitter_y = random.uniform(-jitter_factor, jitter_factor)

            self._move_cursor_instant(x + jitter_x, y + jitter_y)
            time.sleep(random.uniform(0.004, 0.010) * duration_factor)

        # Chốt vị trí cuối cùng
        self._move_cursor_instant(target_x, target_y)

    def hover(self, x=None, y=None, duration=None):
        """Rê chuột tới vị trí và mô phỏng chuột vẫn nhúc nhích nhẹ khi dừng (Human Hover)"""
        if x is not None and y is not None:
            self.move_to(x, y)

        if duration is None:
            duration = random.uniform(0.8, 2.0)

        end_time = time.time() + duration
        while time.time() < end_time:
            drift_x = self.current_pos[0] + random.uniform(-1.5, 1.5)
            drift_y = self.current_pos[1] + random.uniform(-1.5, 1.5)
            self._move_cursor_instant(drift_x, drift_y)
            time.sleep(random.uniform(0.1, 0.3))

    def click(self, x=None, y=None, button="left", clicks=1):
        """Click chuột giống người (có độ trễ phản xạ, thời gian giữ nút chuột)"""
        if x is not None and y is not None:
            self.move_to(x, y)

        curr_x, curr_y = self.current_pos

        for c in range(clicks):
            # Phản xạ dừng chuột trước khi bấm (50 - 120ms)
            time.sleep(random.uniform(0.05, 0.12))

            # Hiệu ứng visual click nếu hiển thị cursor
            if self.show_visual_cursor:
                try:
                    self.driver.execute_script("""
                        const cursor = document.getElementById("__virtual_cursor__");
                        if (cursor) cursor.style.boxShadow = "0 0 10px 5px rgba(255, 0, 0, 0.7)";
                    """)
                except Exception:
                    pass

            self.driver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                {
                    "type": "mousePressed",
                    "x": int(curr_x),
                    "y": int(curr_y),
                    "button": button,
                    "clickCount": c + 1
                }
            )

            # Thời gian đè nút chuột down -> up (40ms - 100ms)
            time.sleep(random.uniform(0.04, 0.10))

            self.driver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                {
                    "type": "mouseReleased",
                    "x": int(curr_x),
                    "y": int(curr_y),
                    "button": button,
                    "clickCount": c + 1
                }
            )

            if self.show_visual_cursor:
                try:
                    self.driver.execute_script("""
                        const cursor = document.getElementById("__virtual_cursor__");
                        if (cursor) cursor.style.boxShadow = "none";
                    """)
                except Exception:
                    pass

            if c < clicks - 1:
                time.sleep(random.uniform(0.08, 0.18))

    def double_click(self, x=None, y=None):
        """Double click giống người"""
        self.click(x, y, button="left", clicks=2)

    def context_click(self, x=None, y=None):
        """Click chuột phải giống người"""
        self.click(x, y, button="right", clicks=1)

    def drag_and_drop(self, start_x, start_y, end_x, end_y):
        """Kéo và thả giống người"""
        self.move_to(start_x, start_y)
        time.sleep(random.uniform(0.1, 0.2))

        self.driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {"type": "mousePressed", "x": int(start_x), "y": int(start_y), "button": "left", "clickCount": 1}
        )
        time.sleep(random.uniform(0.1, 0.25))

        # Kéo với tốc độ chậm hơn
        self.move_to(end_x, end_y, duration_factor=1.8, human_offset=False)
        time.sleep(random.uniform(0.15, 0.3))

        self.driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {"type": "mouseReleased", "x": int(end_x), "y": int(end_y), "button": "left", "clickCount": 1}
        )

    def scroll(self, delta_y, steps=5):
        """Cuộn trang mượt bằng con lăn chuột người dùng"""
        curr_x, curr_y = self.current_pos
        step_delta = delta_y / steps
        for _ in range(steps):
            jitter_delta = step_delta * random.uniform(0.8, 1.2)
            self.driver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                {
                    "type": "mouseWheel",
                    "x": int(curr_x),
                    "y": int(curr_y),
                    "deltaX": 0,
                    "deltaY": jitter_delta
                }
            )
            time.sleep(random.uniform(0.02, 0.06))

    def move_to_element(self, element_or_selector):
        """Di chuyển chuột tới một phần tử HTML (bằng CSS Selector hoặc WebElement)"""
        rect = self._get_element_rect(element_or_selector)
        if not rect:
            raise ValueError(f"Không tìm thấy element: {element_or_selector}")

        # Tọa độ ngẫu nhiên bên trong khung element (tránh luôn bấm chính giữa)
        padding_x = rect["width"] * 0.2
        padding_y = rect["height"] * 0.2

        target_x = random.uniform(rect["left"] + padding_x, rect["right"] - padding_x)
        target_y = random.uniform(rect["top"] + padding_y, rect["bottom"] - padding_y)

        self.move_to(target_x, target_y)
        return target_x, target_y

    def click_element(self, element_or_selector):
        """Di chuyển & click vào phần tử HTML giống người"""
        tx, ty = self.move_to_element(element_or_selector)
        self.click()

    def hover_element(self, element_or_selector, duration=None):
        """Di chuyển & rê chuột trên phần tử HTML giống người"""
        tx, ty = self.move_to_element(element_or_selector)
        self.hover(duration=duration)

    def type_like_human(self, text, element_or_selector=None, error_rate=0.03):
        """Gõ phím mô phỏng người đánh máy: tốc độ ngẫu nhiên, tự động gõ sai & xóa sửa"""
        if element_or_selector:
            self.click_element(element_or_selector)

        keyboard_neighbors = {
            'a': 'qwsz', 'b': 'vghn', 'c': 'xdfv', 'd': 'ersfcx',
            'e': 'wsdr', 'f': 'rtgvcd', 'g': 'tyhbvf', 'h': 'yujnbg',
            'i': 'ujko', 'k': 'ijmlo', 'l': 'opk', 'm': 'njk',
            'n': 'bhjm', 'o': 'iklp', 'p': 'ol', 'r': 'edft',
            's': 'wedxza', 't': 'rfgy', 'u': 'yhji', 'v': 'cfgb',
            'w': 'qase', 'x': 'zsdc', 'y': 'tghu', 'z': 'asx'
        }

        for char in text:
            # Tỷ lệ gõ nhầm ngẫu nhiên
            if random.random() < error_rate and char.lower() in keyboard_neighbors:
                wrong_char = random.choice(keyboard_neighbors[char.lower()])
                self.driver.switch_to.active_element.send_keys(wrong_char)
                time.sleep(random.uniform(0.12, 0.25))
                # Xóa sửa bằng Backspace
                self.driver.switch_to.active_element.send_keys("\b")
                time.sleep(random.uniform(0.1, 0.2))

            self.driver.switch_to.active_element.send_keys(char)

            # Tốc độ gõ phím ngẫu nhiên (chậm hơn khi gặp dấu câu hoặc khoảng trắng)
            if char in ['.', ',', '!', '?']:
                delay = random.uniform(0.3, 0.6)
            elif char == ' ':
                delay = random.uniform(0.12, 0.28)
            else:
                delay = random.uniform(0.04, 0.16)

            time.sleep(delay)

    def _get_element_rect(self, element_or_selector):
        """Lấy vị trí khung hiển thị của phần tử"""
        if isinstance(element_or_selector, str):
            script = """
                const el = document.querySelector(arguments[0]);
                if (!el) return null;
                const r = el.getBoundingClientRect();
                return { left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height };
            """
            return self.driver.execute_script(script, element_or_selector)
        else:
            location = element_or_selector.location_once_scrolled_into_view
            size = element_or_selector.size
            return {
                "left": location["x"],
                "top": location["y"],
                "right": location["x"] + size["width"],
                "bottom": location["y"] + size["height"],
                "width": size["width"],
                "height": size["height"]
            }


# Demo chạy thử nghiệm
if __name__ == "__main__":
    EXE_PATH = "/home/quangminh/Documents/gpm auto/undetected_chromedriver"

    options = uc.ChromeOptions()
    options.add_argument("--window-size=1200,700")

    driver = uc.Chrome(options=options, driver_executable_path=EXE_PATH)

    try:
        driver.get("https://example.com")
        time.sleep(2)

        # Khởi tạo HumanCursor
        human = HumanCursor(driver, show_visual_cursor=True)

        print("--- Demo Human Move ---")
        points = [(100, 100), (300, 150), (500, 300), (700, 200)]
        for x, y in points:
            human.move_to(x, y)
            print(f"Human moved to: ({x}, {y})")
            time.sleep(0.3)

        print("--- Demo Human Hover ---")
        human.hover(400, 250, duration=1.5)

        print("--- Demo Human Click ---")
        human.click(500, 350)

        print("--- Demo Human Context Click (Right Click) ---")
        human.context_click(600, 300)
        time.sleep(1)

        print("--- Demo Human Scroll ---")
        human.scroll(delta_y=200)

        print("--- Demo Human Drag and Drop ---")
        human.drag_and_drop(200, 200, 600, 400)

        print("--- Demo Human Move & Click Element ---")
        try:
            human.click_element("h1")
        except Exception as e:
            print("Element test error:", e)

        time.sleep(3)

    finally:
        driver.quit()