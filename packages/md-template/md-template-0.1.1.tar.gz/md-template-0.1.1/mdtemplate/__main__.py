import argparse


def table_cmd(args):
    kwargs = {
        k: v
        for k, v in {
            "source": args.source,
            "output": args.output,
            "dry_run": args.dry_run,
        }.items()
        if v is not None
    }

    if args.preset == "scoop":
        from mdtemplate.table.presets.scoop import ScoopTableTemplate

        ScoopTableTemplate(**kwargs).render()

    elif args.preset == "userscripts":
        from mdtemplate.table.presets.userscripts import UserscriptsTableTemplate

        UserscriptsTableTemplate(**kwargs).render()


def main():
    def add_global_args(parser_: argparse.ArgumentParser):
        parser_.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="disable writing to the output file",
        )
        return parser_

    parser = add_global_args(
        argparse.ArgumentParser(
            prog="md-template",
            description="Generate a markdown file using a template.",
        )
    )

    ## SUB-COMMANDS ##
    subparsers = parser.add_subparsers()

    parser_table = subparsers.add_parser(
        "table", help="Template a markdown table using a preset"
    )
    parser_table.add_argument(
        "-p",
        "--preset",
        choices=["scoop", "userscripts"],
        required=True,
        help="table preset to use",
    )
    parser_table.add_argument(
        "-s",
        "--source",
        metavar="PATH",
        help="markdown file to read from (default: README.md)",
    )
    parser_table.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="markdown file to write the result to (default: source)",
    )
    add_global_args(parser_table).set_defaults(func=table_cmd)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
