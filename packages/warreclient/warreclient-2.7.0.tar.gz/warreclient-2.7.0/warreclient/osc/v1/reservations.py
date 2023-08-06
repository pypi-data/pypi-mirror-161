#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import logging

from openstackclient.identity import common
from osc_lib.command import command
from osc_lib import utils as osc_utils

from warreclient import exceptions


class ListReservations(command.Lister):
    """List reservations."""

    log = logging.getLogger(__name__ + '.ListReservations')

    def get_parser(self, prog_name):
        parser = super(ListReservations, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help="List all projects reservations (admin only)"
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help="Filter by project (name or ID)"
        )
        parser.add_argument(
            '--project-domain',
            default='default',
            metavar='<project_domain>',
            help='Project domain to filter (name or ID)',
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        client = self.app.client_manager.warre
        kwargs = {}
        if parsed_args.all_projects:
            kwargs['all_projects'] = True
        if parsed_args.project:
            identity_client = self.app.client_manager.identity
            project = common.find_project(
                identity_client,
                common._get_token_resource(identity_client, 'project',
                                           parsed_args.project),
                parsed_args.project_domain,
            )

            kwargs['project_id'] = project.id
            # Assume all_projects if project set
            kwargs['all_projects'] = True

        reservations = client.reservations.list(**kwargs)
        columns = ['id', 'status', 'flavor', 'start', 'end']
        for r in reservations:
            r.flavor = r.flavor.name
        return (
            columns,
            (osc_utils.get_item_properties(q, columns) for q in reservations)
        )


class ReservationCommand(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(ReservationCommand, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            metavar='<id>',
            help=('ID of reservation')
        )
        return parser


class ShowReservation(ReservationCommand):
    """Show reservation details."""

    log = logging.getLogger(__name__ + '.ShowReservation')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        client = self.app.client_manager.warre
        try:
            reservation = client.reservations.get(parsed_args.id)
        except exceptions.NotFound as ex:
            raise exceptions.CommandError(str(ex))

        return self.dict2columns(reservation.to_dict())


class CreateReservation(command.ShowOne):
    """Create a reservation."""

    log = logging.getLogger(__name__ + '.CreateReservation')

    def get_parser(self, prog_name):
        parser = super(CreateReservation, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            help="Flavor"
        )
        parser.add_argument(
            '--start',
            metavar='<start>',
            help='Time (YYYY-MM-DD HH:MM) UTC TZ for starting the lease',
            required=True,
        )
        parser.add_argument(
            '--end',
            metavar='<end>',
            required=True,
            help='Time (YYYY-MM-DD HH:MM) UTC TZ for ending the lease '
                 '(default: 24h from now)',
        )
        parser.add_argument(
            '--instance-count',
            metavar='<instance-count>',
            type=int,
            default=1,
            help="Number of instances (Default: 1)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        client = self.app.client_manager.warre
        flavor = osc_utils.find_resource(
            client.flavors,
            parsed_args.flavor,
            all_projects=True)

        fields = {'flavor_id': flavor.id,
                  'start': parsed_args.start,
                  'end': parsed_args.end,
                  'instance_count': parsed_args.instance_count}

        reservation = client.reservations.create(**fields)
        reservation_dict = reservation.to_dict()
        return self.dict2columns(reservation_dict)


class DeleteReservation(ReservationCommand):
    """Delete reservation."""

    log = logging.getLogger(__name__ + '.DeleteReservation')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        client = self.app.client_manager.warre
        try:
            client.reservations.delete(parsed_args.id)
        except exceptions.NotFound as ex:
            raise exceptions.CommandError(str(ex))

        return [], []
