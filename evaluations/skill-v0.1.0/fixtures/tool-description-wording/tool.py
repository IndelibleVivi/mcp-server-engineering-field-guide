TOOL = {
    "name": "notes_lookup",
    "description": "Does note things for a key.",
    "inputSchema": {
        "type": "object",
        "properties": {"key": {"type": "string"}},
        "required": ["key"],
        "additionalProperties": False,
    },
}
