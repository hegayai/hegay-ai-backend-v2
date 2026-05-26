# pricing/plans.py

PLANS = {
    "Free": {
        "price": 0,
        "resolution": "512x512",
        "images": 2,
        "videos": 0,
        "video_seconds": 0,
        "chat_messages": 20,
        "canvas_limit": 0,
        "tools": "none",
        "commercial": False
    },

    "Starter": {
        "price": 15,
        "resolution": "768x768",
        "images": 10,
        "videos": 1,
        "video_seconds": 5,
        "chat_messages": 300,
        "canvas_limit": 5,
        "tools": "basic",
        "commercial": False
    },

    "Creator": {
        "price": 29,
        "resolution": "1024x1024",
        "images": 40,
        "videos": 2,
        "video_seconds": 6,
        "chat_messages": 1000,
        "canvas_limit": 10,
        "tools": "medium",
        "commercial": False
    },

    "Pro": {
        "price": 59,
        "resolution": "1024x1024",
        "images": 120,
        "videos": 5,
        "video_seconds": 8,
        "chat_messages": 3000,
        "canvas_limit": 20,
        "tools": "full",
        "commercial": False
    },

    "Studio": {
        "price": 99,
        "resolution": "1024x1024",
        "images": 250,
        "videos": 10,
        "video_seconds": 10,
        "chat_messages": 10000,
        "canvas_limit": 40,
        "tools": "full+",
        "commercial": True
    }
}
