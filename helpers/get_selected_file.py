def get_selected_file_path(input: str) -> str:
    if input == "":
        return ""
    return f"Выбранный файл:\n{input.split('/')[-1]}"
