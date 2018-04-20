# Copyright(c) 2016 Nippon Telegraph and Telephone Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import sys

from oslo_utils import encodeutils
import six

import masakariclient
from masakariclient import cliargs
from masakariclient import client as masakari_client
from masakariclient.common import exception as exc
from masakariclient.common.i18n import _
from masakariclient.common import utils

USER_AGENT = 'python-masakariclient'
LOG = logging.getLogger(__name__)


class MasakariShell(object):
    def __init__(self):
        pass

    def do_bash_completion(self, args):
        """All of the commands and options to stdout."""
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            if sc_str == 'bash_completion' or sc_str == 'bash-completion':
                continue

            commands.add(sc_str)
            for option in list(sc._optionals._option_string_actions):
                options.add(option)

        print(' '.join(commands | options))

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser('bash_completion',
                                          add_help=False,
                                          formatter_class=HelpFormatter)

        subparser.set_defaults(func=self.do_bash_completion)
        self.subcommands['bash_completion'] = subparser

    def _get_subcommand_parser(self, base_parser, version):
        parser = base_parser

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        submodule = utils.import_versioned_module(version, 'shell')
        self._find_actions(subparsers, submodule)
        self._add_bash_completion_subparser(subparsers)

        return parser

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)

            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command,
                                              help=help,
                                              description=desc,
                                              add_help=False,
                                              formatter_class=HelpFormatter)

            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS)

            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

            self.subcommands[command] = subparser

    def _setup_masakari_client(self, api_ver, args):
        """Create masakari client using given args."""
        kwargs = {
            'auth_plugin': args.auth_plugin or 'password',
            'auth_url': args.auth_url,
            'project_name': args.project_name or args.tenant_name,
            'project_id': args.project_id or args.tenant_id,
            'domain_name': args.domain_name,
            'domain_id': args.domain_id,
            'project_domain_name': args.project_domain_name,
            'project_domain_id': args.project_domain_id,
            'user_domain_name': args.user_domain_name,
            'user_domain_id': args.user_domain_id,
            'username': args.username,
            'user_id': args.user_id,
            'password': args.password,
            'verify': args.verify,
            'token': args.token,
            'trust_id': args.trust_id,
            'interface': args.interface,
            'region_name': args.region_name,
        }

        return masakari_client.Client(api_ver, user_agent=USER_AGENT, **kwargs)

    def _setup_logging(self, debug):
        if debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.WARNING
        log_format = "%(levelname)s (%(module)s) %(message)s"
        logging.basicConfig(format=log_format, level=log_level)
        logging.getLogger('iso8601').setLevel(logging.WARNING)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

    def main(self, argv):

        parser = argparse.ArgumentParser(
            prog='masakari',
            description="masakari shell",
            epilog='Type "masakari help <COMMAND>" for help on a specific '
            'command.',
            add_help=False,
        )
        # add add arguments
        cliargs.add_global_args(parser, masakariclient.__version__)
        cliargs.add_global_identity_args(parser)

        # parse main arguments
        (options, args) = parser.parse_known_args(argv)

        self._setup_logging(options.debug)

        base_parser = parser
        api_ver = options.masakari_api_version

        # add subparser
        subcommand_parser = self._get_subcommand_parser(base_parser, api_ver)
        self.parser = subcommand_parser

        # --help/-h or no arguments
        if not args and options.help or not argv:
            self.do_help(options)
            return 0

        args = subcommand_parser.parse_args(argv)

        sc = self._setup_masakari_client(api_ver, args)
        # call specified function
        args.func(sc.service, args)

    @utils.arg('command', metavar='<subcommand>', nargs='?',
               help=_('Display help for <subcommand>.'))
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


def main(args=None):
    try:
        if args is None:
            args = sys.argv[1:]

        MasakariShell().main(args)
    except KeyboardInterrupt:
        print(_("KeyboardInterrupt masakari client"), sys.stderr)
        return 130
    except Exception as e:
        if '--debug' in args or '-d' in args:
            raise
        else:
            print(encodeutils.safe_encode(six.text_type(e)), sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
