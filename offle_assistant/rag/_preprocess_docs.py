import pathlib
import sys

from prompt_toolkit import print_formatted_text as fprint
import pymupdf4llm


def preprocess_docs(
    rag_dir: pathlib.Path,
    overwrite: bool = False
):
    src_dir: pathlib.Path = pathlib.Path(rag_dir, "src/")

    if not src_dir.exists():
        fprint(f"❌ Directory does not exist: {src_dir}")
        sys.exit(1)

    try:
        file_list: list[pathlib.Path] = []
        for file in src_dir.rglob('*'):
            if file.is_file():
                file_list.append(file.resolve())
    except Exception as e:
        print(f"Exception occurred: {e}")

    try:
        processed_files_dir: pathlib.Path = pathlib.Path(
            rag_dir,
            "processed_files/"
        )
        processed_files_dir.mkdir(parents=False, exist_ok=True)
    except Exception as e:
        print(
            f"Exception occurred while creating processed files directory: {e}"
        )
        sys.exit(1)

    """
        If I want to parallelize this, I need to be sure I don't accidentally
        write to the same file twice. Hypothetically, you could have two
        files with the same name but different formats in the src/ dir
        (eg: file_a.pdf and file_a.epub). They would then both be written to
        file_a.md, potentially at the exact same time. Not good.
        Probably, I collect output file names first because that should be
        quick, and then I can perform that check in the loop. If all goes
        well, then we can parallelize safely.
    """
    for file in file_list:
        filename: str = file.stem
        processed_file_path: pathlib.Path = pathlib.Path(
            processed_files_dir,
            filename + ".md"
        )
        if (processed_file_path.exists()) and (overwrite is False):
            fprint(
                f"Skipping {file.name}, file already exists: "
                f"{processed_file_path}"
            )
        else:  # If the file does not exist or if overwrite is True
            md_text: str = pymupdf4llm.to_markdown(file)
            processed_file_path.write_bytes(md_text.encode())
