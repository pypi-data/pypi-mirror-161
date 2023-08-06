import click
from pathlib import Path


def validate_out_path(ctx: click.Context, param: click.Parameter, out_path: Path):
    if out_path is None:
        return _resolve_unspecified_out_path(ctx, param)
    if not out_path.exists():
        return _resolve_nonexisting_out_path(ctx, param, out_path)
    if out_path.is_file():  # <- exists as well
        return _validate_file_out_path(ctx, param, out_path)
    if out_path.is_dir():
        return _validate_dir_out_path(ctx, param, out_path)
    raise click.BadParameter(
        f"{param.human_readable_name} must be a file or directory: {out_path}", ctx, param
    )


def _resolve_unspecified_out_path(ctx: click.Context, param: click.Parameter) -> Path:
    if not ctx.params.get("overwrite"):
        raise click.BadParameter(
            f"{param.human_readable_name} is required if OVERWRITE is not set", ctx, param
        )
    return ctx.params["in_path"]


def _resolve_nonexisting_out_path(
    ctx: click.Context, param: click.Parameter, out_path: Path
) -> Path:
    """Specified but does not exist on file system, whether dir or file.
    Note that this means OUT_PATH is necessarily a different path than IN_PATH."""
    in_path: Path = ctx.params["in_path"]
    if in_path.is_dir():
        if not click.confirm(
            f"{param.human_readable_name} does not exist; create? {str(out_path)!r}"
        ):
            raise click.Abort()
        out_path.mkdir(parents=True)
    return out_path


def _validate_file_out_path(
    ctx: click.Context, param: click.Parameter, out_path: Path
) -> Path:
    if ctx.params["in_path"].is_dir():
        raise click.BadParameter(
            f"{param.human_readable_name} must be a directory if IN_PATH is a directory",
            ctx,
            param,
        )
    if ctx.params.get("overwrite"):
        return out_path
    if click.confirm(f"{param.human_readable_name} exists; overwrite? {str(out_path)!r}"):
        return out_path
    raise click.Abort()


def _validate_dir_out_path(
    ctx: click.Context, param: click.Parameter, out_path: Path
) -> Path:
    in_path: Path = ctx.params["in_path"]
    overwrite_out_paths = []
    simple_write_out_paths = []
    if in_path.is_file():
        out_file = out_path / in_path.name
        if out_file.is_dir():
            raise click.BadParameter(
                f"Out file is a directory, but IN_PATH is a file.\n"
                f"Out file: {out_file}\n"
                f"In path: {in_path}",
                ctx,
                param,
            )
        if out_file.exists():
            if ctx.params.get("overwrite"):
                return out_path
            overwrite_out_paths.append(out_file)
        else:
            simple_write_out_paths.append(out_file)
    else:
        click.echo(f"Not implemented directory input! got {in_path}", err=True)
        raise click.Abort()

    if not overwrite_out_paths:
        return out_path

    if not click.confirm(
        f"Overwrite {len(overwrite_out_paths)} files? Specifically: \n"
        "\n".join(str(path) for path in overwrite_out_paths)
    ):
        raise click.Abort()
    return out_path


def validate_in_path(ctx: click.Context, param: click.Parameter, in_path: Path):
    if in_path.is_dir():
        click.echo(f"Not implemented directory input! got {in_path}", err=True)
        raise click.Abort()
    return in_path
