import os
from src.parser import parse_file
from src.cleaner import process_raw_email

def handle_file(filepath):
    raw = parse_file(filepath)
    if raw is None:
        return None
    return process_raw_email(raw, os.path.basename(filepath))
  
