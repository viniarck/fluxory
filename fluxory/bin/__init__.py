#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from fluxory.__version__ import version
from fluxory.controller import OpenFlowController
import logging
import logging.config
import asyncio
import sys
import os
log = logging.getLogger(__name__)


def main() -> None:
    """main function."""
    parser = argparse.ArgumentParser(description="fluxory")
    parser.add_argument(
        "-p", "--port", default=6653, help="OpenFlow port (default: 6653)"
    )
    parser.add_argument(
        "-l",
        "--level",
        choices=["error", "info", "debug"],
        default="info",
        help="logging verbosity level (default: info)",
    )
    parser.add_argument(
        "--log-file",
        default="/home/viniarck/repos/ryu/logging.ini",
        help="logging verbosity level (default: info)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="{}".format(version),
        help="show version",
    )
    env = os.environ
    args = parser.parse_args()
    if os.path.isfile(args.log_file):
        logging.config.fileConfig(args.log_file)
    else:
        # TODO provide default log config
        logging.basicConfig(level=logging.INFO)

    debug = env.get("FLUXORY_DEBUG") or args.level

    try:
        c = OpenFlowController(1, 3, 4, 5, 6)
        asyncio.run(c.run())
    except KeyboardInterrupt:
        log.info("C-c")
        sys.exit(1)
    except Exception as e:
        if "debug" in debug:
            raise
        else:
            log.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
