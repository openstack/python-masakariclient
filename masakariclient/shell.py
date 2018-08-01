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
import importlib
import logging
from oslo_utils import encodeutils
from oslo_utils import importutils
import pbr.version
import pyclbr
import six
import sys
import warnings

import masakariclient
from masakariclient import cliargs
from masakariclient import client as masakari_client
from masakariclient.common import exception as exc
from masakariclient.common.i18n import _
from masakariclient.common import utils

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
        }

        return masakari_client.Client(api_ver, **kwargs)

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

        # From openstacksdk version 0.11.1 onwards, there is no way
        # you can add service to the connection. Hence we need to monkey patch
        # _find_service_filter_class method from sdk to allow to point to the
        # correct service filter class implemented in masakariclient.
        sdk_ver = pbr.version.VersionInfo('openstacksdk').version_string()
        if sdk_ver in ['0.11.1', '0.11.2', '0.11.3']:
            monkey_patch_for_openstacksdk("openstack._meta:masakariclient."
                                          "shell."
                                          "masakari_service_filter_class")
        if sdk_ver in ['0.12.0']:
            monkey_patch_for_openstacksdk("openstack._meta.connection:"
                                          "masakariclient.shell."
                                          "masakari_service_filter_class")
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


def monkey_patch_for_openstacksdk(module_and_decorator_name):
    module, decorator_name = module_and_decorator_name.split(':')
    # import decorator function
    decorator = importutils.import_class(decorator_name)
    __import__(module)
    # Retrieve module information using pyclbr
    module_data = pyclbr.readmodule_ex(module)
    for key in module_data.keys():
        # set the decorator for the class methods
        if isinstance(module_data[key], pyclbr.Function):
            if key == "_find_service_filter_class":
                setattr(sys.modules[module], key, decorator)


def masakari_service_filter_class(service_type):
    package_name = 'openstack.{service_type}'.format(
        service_type=service_type).replace('-', '_')
    module_name = service_type.replace('-', '_') + '_service'
    class_name = ''.join(
        [part.capitalize() for part in module_name.split('_')])
    try:
        import_name = '.'.join([package_name, module_name])
        if (class_name == "InstanceHaService" and
                import_name == "openstack.instance_ha."
                               "instance_ha_service"):
            class_name = "HAService"
            import_name = "masakariclient.sdk.ha.ha_service"

        service_filter_module = importlib.import_module(import_name)
    except ImportError as e:
        # ImportWarning is ignored by default. This warning is here
        # as an opt-in for people trying to figure out why something
        # didn't work.
        warnings.warn(
            "Could not import {service_type} service filter: {e}".format(
                service_type=service_type, e=str(e)),
            ImportWarning)
        return None
    # There are no cases in which we should have a module but not the class
    # inside it.
    service_filter_class = getattr(service_filter_module, class_name)
    return service_filter_class

if __name__ == "__main__":
    sys.exit(main())
