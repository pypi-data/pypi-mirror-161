from __future__ import annotations

import argparse
import itertools
import re
from typing import Sequence

from prepare_commit_msg.template import get_rendered_template
from prepare_commit_msg.template import get_template
from prepare_commit_msg.util import cmd_output


def get_current_branch() -> str:
    ref_name = cmd_output('git', 'symbolic-ref', '--short', 'HEAD')

    return ref_name.strip()


def _configure_args(
        parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    parser.add_argument(
        '-t', '--template', default='prepare_commit_msg_append.j2',
        help='Template to use for the commit message. Absolute file name or'
             'the name of one the bundled in the package template directory',
    )
    parser.add_argument(
        '-b', '--branch', action='append', default=['main', 'master'],
        help='Branch to skip, may be specified multiple times.',
    )
    parser.add_argument(
        '-p', '--pattern', action='append', default=['(?<=feature/).*'],
        help='RegEx Pattern for recognising Ticket Numbers in branch, '
             'may be specified multiple times.',
    )
    parser.add_argument('COMMIT_MSG_FILE', nargs=argparse.REMAINDER)

    return parser


def update_commit_file(
        commit_msg_file: str,
        template: str,
        ticket: str,
        source: str | None,
) -> int:
    try:
        with open(commit_msg_file) as f:
            data = f.readlines()

        original = list(
            itertools.takewhile(
                lambda line: not line.startswith('#'), data,
            ),
        )

        rest = data[len(original):]

        # As docs states: ...the source of the commit message, and can be:
        # * message (if a -m or -F option was given);
        # * template (if a -t option was given or the configuration option
        #   commit.template is set);
        # * merge (if the commit is a merge or a .git/MERGE_MSG file exists);
        # * squash (if a .git/SQUASH_MSG file exists); or
        # * commit, followed by a commit object name (if a -c, -C or --amend
        #   option was given).
        should_update_file = (
            # per design only in those 3 cases we update message
            source == 'message' or source == 'merge' or source is None
        )
        if not should_update_file:
            return 0

        variables = {
            'ticket': ticket,
            'original': original,
            'rest': rest,
            'full': data,
        }

        content = get_rendered_template(
            template=template,
            variables=variables,
        )
        with open(commit_msg_file, 'w') as f:
            f.write(content)

        return 0
    except OSError as err:
        print(f'OS error: {err}')
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = _configure_args(argparse.ArgumentParser())
    args = parser.parse_args(argv)

    current = get_current_branch()
    branches = frozenset(args.branch)
    if current in branches:
        # checked allowed branches
        return 0

    patterns = frozenset(args.pattern)
    matches = [
        match.group(0)
        for match in (re.search(pattern, current) for pattern in patterns)
        if match
    ]
    if len(matches) == 0:
        # checked allowed branches
        return 0

    extra_args = args.COMMIT_MSG_FILE
    commit_file = extra_args[0]
    source = None if len(extra_args) <= 1 else extra_args[1]
    template = get_template(args.template)
    return update_commit_file(commit_file, template, matches[0], source)


if __name__ == '__main__':
    raise SystemExit(main())
