# pricing/pricing.py

# -----------------------------
# GPU COST CONSTANTS (DeepSeek)
# -----------------------------

IMAGE_COST_PER_UNIT = 0.08          # $0.08 per image (any resolution)
VIDEO_COST_PER_SECOND = {
    "480p": 0.22,                   # $0.22 per second
    "720p": 0.30,                   # $0.30 per second
    "1080p": 0.45                   # $0.45 per second
}

CHAT_COST_PER_MESSAGE = 0.0002      # $0.0002 per message
CANVAS_COST_PER_ACTION = 0.05       # $0.05 per canvas AI operation

# -----------------------------
# IMAGE COST
# -----------------------------

def calculate_image_cost(num_images: int) -> float:
    return num_images * IMAGE_COST_PER_UNIT

# -----------------------------
# VIDEO COST
# -----------------------------

def calculate_video_cost(seconds: int, resolution: str) -> float:
    rate = VIDEO_COST_PER_SECOND.get(resolution, VIDEO_COST_PER_SECOND["720p"])
    return seconds * rate

# -----------------------------
# CHAT COST
# -----------------------------

def calculate_chat_cost(messages: int) -> float:
    return messages * CHAT_COST_PER_MESSAGE

# -----------------------------
# CANVAS COST
# -----------------------------

def calculate_canvas_cost(actions: int) -> float:
    return actions * CANVAS_COST_PER_ACTION

# -----------------------------
# TOTAL COST
# -----------------------------

def calculate_total_cost(images=0, videos=None, chat=0, canvas=0):
    videos = videos or []

    total = 0
    total += calculate_image_cost(images)
    total += sum(calculate_video_cost(v["seconds"], v["resolution"]) for v in videos)
    total += calculate_chat_cost(chat)
    total += calculate_canvas_cost(canvas)

    return round(total, 4)
