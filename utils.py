def is_tool(tool: str) -> bool:
    from shutil import which
    return which(tool) is not None