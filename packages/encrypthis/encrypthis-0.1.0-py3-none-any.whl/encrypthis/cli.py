#!.venv/bin/python3
# see for salt+hash:
# https://stackoverflow.com/a/23768422
import sys
import textwrap
from pathlib import Path

# pip install cryptography
import click
from cryptography.fernet import Fernet

from .validators import validate_in_path, validate_out_path

ENCRYPT_EXTENSION_WHITELIST = {".py", ".txt", ".md", ".rst", ""}

IN_PATH_HELP = (
    "Path to file or directory, or glob pattern, to encrypt. "
    f"If directory, all text files with extensions {ENCRYPT_EXTENSION_WHITELIST} in directory will be encrypted."
)

OUT_PATH_HELP = (
    "Path to output the encrypted file(s). "
    "If IN_PATH is a directory or glob, OUT_PATH must be a directory as well."
)

ENCRYPT_HELP = textwrap.dedent(
    f"""\b\bArguments: 
IN_PATH:
{IN_PATH_HELP}
OUT_PATH:
{OUT_PATH_HELP}"""
).replace("\n", "\n\n")


@click.command(
    no_args_is_help=True,
    help=ENCRYPT_HELP,
)
@click.argument(
    "command",
    type=click.Choice(["encrypt", "decrypt"]),
)
@click.argument(
    "in_path",
    type=click.Path(exists=True, readable=True, resolve_path=True, path_type=Path),
    callback=validate_in_path,
)
@click.argument(
    "out_path",
    type=click.Path(resolve_path=True, path_type=Path),
    required=False,
    callback=validate_out_path,
)
@click.option(
    "--key",
    "-k",
    "encryption_key",
    prompt="Encryption key",
    envvar="ENCRYPTHIS_KEY",
    show_envvar=True,
    callback=lambda ctx, param, value: value.encode(),
)
@click.option(
    "-w", "--overwrite", is_flag=True, help="Overwrite existing files", is_eager=True
)
def main(
    command, in_path: Path, out_path: Path, encryption_key: bytes, overwrite: bool = False
):
    fernet: Fernet = Fernet(encryption_key)
    if command == "encrypt":
        encrypt(fernet, in_path, out_path, encryption_key, overwrite)
    elif command == "decrypt":
        decrypt(fernet, in_path, out_path, encryption_key, overwrite)


def encrypt(
    fernet: Fernet,
    in_path: Path,
    out_path: Path,
    encryption_key: bytes,
    overwrite: bool = False,
):
    if not click.confirm(
        f"Encrypting:  {str(in_path)!r}\n"
        f"Output path: {str(out_path)!r}\n"
        f"Continue?"
    ):
        raise click.Abort()
    encrypted_data = get_encrypted_file_data(in_path, fernet)
    write_data(encrypted_data, out_path, in_path)
    click.echo(f"Encrypted {in_path} to {out_path}")


def decrypt(
    fernet: Fernet,
    in_path: Path,
    out_path: Path,
    encryption_key: bytes,
    overwrite: bool = False,
):
    if not click.confirm(
        f"Decrypting:  {str(in_path)!r}\n"
        f"Output path: {str(out_path)!r}\n"
        f"Continue?"
    ):
        raise click.Abort()
    decrypted_data = get_decrypted_file_data(in_path, fernet)
    write_data(decrypted_data, out_path, in_path)
    click.echo(f"Decrypted {in_path} to {out_path}")


def get_encrypted_file_data(path, fernet: Fernet) -> bytes:
    bytes_content = Path(path).read_bytes()
    encrypted_data = fernet.encrypt(bytes_content)
    return encrypted_data


def get_decrypted_file_data(path, fernet: Fernet) -> bytes:
    bytes_content = Path(path).read_bytes()
    decrypted_data = fernet.decrypt(bytes_content)
    return decrypted_data


def write_data(data: bytes, out_path, in_path):
    out_path = Path(out_path)
    if out_path.is_dir():
        return Path(out_path / in_path.name).write_bytes(data)
    return Path(out_path).write_bytes(data)


def iter_encrypted_dir_files(in_path: Path, fernet: Fernet):
    for path in in_path.rglob("*"):
        if (
            path.is_file()
            and path.suffix in ENCRYPT_EXTENSION_WHITELIST
            and not any(part.startswith(".") for part in path.parts)
        ):
            encrypted = get_encrypted_file_data(path, fernet)
            yield path, encrypted


def encrypt_cli():
    sys.argv.insert(1, "encrypt")
    return main()


def decrypt_cli():
    sys.argv.insert(1, "decrypt")
    return main()


if __name__ == "__main__":
    main()
