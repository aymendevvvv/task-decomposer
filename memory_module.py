from config import config


def load_memory():
    try:
        with open(config.MEMORY_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return []


def save_memory(lines):
    with open(config.MEMORY_FILE, "w") as f:
        for line in lines:
            f.write(line + "\n")


def add_memory(text):
    text = text.replace("@memadd", "").strip()
    mem = load_memory()
    mem.append(text)
    save_memory(mem)


def remove_memory(index):
    mem = load_memory()

    try:
        index = int(index)
        if 0 <= index < len(mem):
            mem.pop(index)
            save_memory(mem)
    except:
        pass


def get_memory_tasks():
    mem = load_memory()
    return mem