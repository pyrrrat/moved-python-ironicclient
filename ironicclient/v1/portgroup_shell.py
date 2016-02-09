# Copyright 2015 SAP Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from ironicclient.common import cliutils
from ironicclient.common import utils
from ironicclient.v1 import resource_fields as res_fields


def _print_portgroup_show(portgroup, fields=None):
    if fields is None:
        fields = res_fields.PORTGROUP_DETAILED_RESOURCE.fields

    data = dict([(f, getattr(portgroup, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'portgroup',
    metavar='<id>',
    help="UUID of the portgroup (or MAC address if --address is specified).")
@cliutils.arg(
    '--address',
    dest='address',
    action='store_true',
    default=False,
    help='<id> is the MAC address (instead of the UUID) of the port group.')
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more portgroup fields. Only these fields will be fetched "
         "from the server.")
def do_portgroup_show(cc, args):
    """Show detailed information about a portgroup."""
    fields = args.fields[0] if args.fields else None
    utils.check_for_invalid_fields(
        fields, res_fields.PORTGROUP_DETAILED_RESOURCE.fields)
    if args.address:
        portgroup = cc.portgroup.get_by_address(args.portgroup, fields=fields)
    else:
        utils.check_empty_arg(args.portgroup, '<id>')
        portgroup = cc.portgroup.get(args.portgroup, fields=fields)
    _print_portgroup_show(portgroup, fields=fields)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about port groups.")
@cliutils.arg(
    '-n', '--node',
    dest='node',
    metavar='<node>',
    help='UUID of the node that this port group belongs to.')
@cliutils.arg(
    '--address',
    metavar='<mac-address>',
    help='Only show information for the port group with this MAC address.')
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of port groups to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<portgroup>',
    help='Port group UUID (for example, of the last port group in the list '
         'from a previous request). '
         'Returns the list of ports after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Port group field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more portgroup fields. Only these fields will be fetched "
         "from the server. Can not be used when '--detail' is specified.")
def do_portgroup_list(cc, args):
    """List the port groups."""
    params = {}

    if args.address is not None:
        params['address'] = args.address
    if args.node is not None:
        params['node'] = args.node

    if args.detail:
        fields = res_fields.PORTGROUP_DETAILED_RESOURCE.fields
        field_labels = res_fields.PORTGROUP_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.PORTGROUP_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.PORTGROUP_RESOURCE.fields
        field_labels = res_fields.PORTGROUP_RESOURCE.labels

    sort_fields = res_fields.PORTGROUP_DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.PORTGROUP_DETAILED_RESOURCE.sort_labels

    params.update(utils.common_params_for_list(args,
                                               sort_fields,
                                               sort_field_labels))

    portgroup = cc.portgroup.list(**params)
    cliutils.print_list(portgroup, fields,
                        field_labels=field_labels,
                        sortby_index=None)


@cliutils.arg(
    '-a', '--address',
    metavar='<address>',
    required=True,
    help='MAC address for this port group.')
@cliutils.arg(
    '-n', '--node', '--node_uuid',
    dest='node_uuid',
    metavar='<node>',
    required=True,
    help='UUID of the node that this port group belongs to.')
@cliutils.arg(
    '--name',
    metavar="<name>",
    help='Name for the portgroup.')
@cliutils.arg(
    '-e', '--extra',
    metavar="<key=value>",
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times.")
def do_portgroup_create(cc, args):
    """Create a new port group."""
    field_list = ['address', 'extra', 'node_uuid', 'name']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    portgroup = cc.portgroup.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(portgroup, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg('portgroup', metavar='<portgroup>', nargs='+',
              help="UUID of the portgroup.")
def do_portgroup_delete(cc, args):
    """Delete a portgroup."""
    for p in args.portgroup:
        cc.portgroup.delete(p)
        print('Deleted portgroup %s' % p)


@cliutils.arg('portgroup', metavar='<portgroup>',
              help="UUID of the portgroup.")
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operation: 'add', 'replace', or 'remove'.")
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attribute to add, replace, or remove. Can be specified multiple  "
         "times. For 'remove', only <path> is necessary.")
def do_portgroup_update(cc, args):
    """Update information about a portgroup."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    portgroup = cc.portgroup.update(args.portgroup, patch)
    _print_portgroup_show(portgroup)
