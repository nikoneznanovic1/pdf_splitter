# routes_config.py

ALL_STATIC_PAGES = [
    {"path": "/",          "priority": "1.0", "changefreq": "daily"},
    {"path": "/featured",  "priority": "0.8", "changefreq": "weekly"},
    {"path": "/blog",      "priority": "0.8", "changefreq": "weekly"},
    {"path": "/privacy",   "priority": "0.4", "changefreq": "yearly"},
    {"path": "/terms",     "priority": "0.4", "changefreq": "yearly"},
]

ALL_TOOLS = [
    {"path": "/merge-pdf",      "priority": "0.9", "changefreq": "monthly"},
    {"path": "/split-pdf",      "priority": "0.9", "changefreq": "monthly"},
    {"path": "/compress-pdf",   "priority": "0.9", "changefreq": "monthly"},
    {"path": "/convert-pdf",    "priority": "0.9", "changefreq": "monthly"},
    {"path": "/watermark-pdf",  "priority": "0.9", "changefreq": "monthly"},
    
    # NOVO:
    {"path": "/word-to-pdf",    "priority": "0.9", "changefreq": "monthly"},
    {"path": "/pdf-to-word",    "priority": "0.9", "changefreq": "monthly"},
]

ALL_BLOG_POSTS = [
    {"path": "/blog/how-to-merge-pdfs",              "priority": "0.7", "changefreq": "monthly"},
    {"path": "/blog/top-free-pdf-editors",           "priority": "0.7", "changefreq": "monthly"},
    {"path": "/blog/how-to-compress-pdfs",           "priority": "0.7", "changefreq": "monthly"},
    {"path": "/blog/how-to-split-pdf-online-guide",  "priority": "0.7", "changefreq": "monthly"},
    {"path": "/blog/best-ai-pdf-tools-2025",         "priority": "0.7", "changefreq": "monthly"},
]

def get_all_urls():
    return ALL_STATIC_PAGES + ALL_TOOLS + ALL_BLOG_POSTS
