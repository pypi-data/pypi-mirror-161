try:
    from otlet_cli.cli import run_cli # type: ignore
    run_cli()
except ImportError:
    import sys
    print("Package otlet-cli not found. Please download otlet-cli to run.", file=sys.stderr)
    raise SystemExit(1)