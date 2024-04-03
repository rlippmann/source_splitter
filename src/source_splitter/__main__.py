"""Source splitter main file."""

import argparse
from pathlib import Path
from . import ss_exceptions
from . import ss_languages
from . import ss_filesplitters


def process_file(file_path: Path, output_dir: Path):
    """Process a single file."""
    try:
        file_instance = ss_languages.get_class_for_file(file_path)
        splitter = ss_filesplitters.get_file_splitter(file_instance, output_dir)
        splitter.split_file()
    except OSError as o:
        print(f"OS Error processing file: {file_path}: {o}, skipping...")
    except ss_exceptions.SSNoLanguageFound as e:
        print(f"No language found for file: {file_path}: {e}, skipping...")
    except ss_exceptions.SSParseFailed as e:
        print(f"Parse failed for file: {file_path}: {e}, skipping...")
    print(f"Processed file: {file_path} -> {output_dir}")


def process_directory(directory_path: Path, output_dir: Path):
    """Process a directory."""
    for file_path in directory_path.iterdir():
        if file_path.is_file():
            process_file(file_path, output_dir)
        elif file_path.is_dir():
            process_directory(file_path, output_dir)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process files or directories")
    parser.add_argument("input_path", help="Path to the input file or directory")
    parser.add_argument("output_dir", help="Path to the output directory")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_dir = Path(args.output_dir)

    if input_path.is_file():
        process_file(input_path, output_dir)
    elif input_path.is_dir():
        process_directory(input_path, output_dir)
    else:
        print("Invalid file or directory path")


if __name__ == "__main__":
    main()
