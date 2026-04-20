TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate the browser to a URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to navigate to"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "click",
        "description": "Click at specific coordinates on the page. Use the screenshot to identify where to click.",
        "input_schema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate (pixels from left)"},
                "y": {"type": "integer", "description": "Y coordinate (pixels from top)"},
            },
            "required": ["x", "y"],
        },
    },
    {
        "name": "type_text",
        "description": "Type text into the currently focused element. Click on an input field first if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to type"},
                "press_enter": {
                    "type": "boolean",
                    "description": "Whether to press Enter after typing",
                    "default": False,
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "press_key",
        "description": "Press a keyboard key or key combination (e.g. 'Enter', 'Tab', 'Meta+a', 'Backspace').",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key or combination to press"},
            },
            "required": ["key"],
        },
    },
    {
        "name": "scroll",
        "description": "Scroll the page up or down.",
        "input_schema": {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["up", "down"],
                    "description": "Scroll direction",
                },
                "amount": {
                    "type": "integer",
                    "description": "Pixels to scroll (default 500)",
                    "default": 500,
                },
            },
            "required": ["direction"],
        },
    },
    {
        "name": "wait",
        "description": "Wait for a specified number of seconds (useful for pages to load).",
        "input_schema": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "number",
                    "description": "Seconds to wait (max 10)",
                },
            },
            "required": ["seconds"],
        },
    },
    {
        "name": "extract_data",
        "description": "Extract and store structured data from the current page. Use this to capture information you've read (e.g. vulnerability details, message contents) before calling done.",
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Structured data extracted from the page",
                },
            },
            "required": ["data"],
        },
    },
    {
        "name": "done",
        "description": "Signal that the task is complete. Provide a summary of what was accomplished.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Summary of what was accomplished",
                },
            },
            "required": ["summary"],
        },
    },
]
