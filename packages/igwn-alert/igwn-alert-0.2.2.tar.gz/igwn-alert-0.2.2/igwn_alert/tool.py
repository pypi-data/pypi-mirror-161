# Copyright (C) Alexander Pace (2021)
# Copyright (C) Duncan Meacher (2021)
#
# This file is part of igwn_alert
#
# igwn_alert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with igwn_alert.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import argparse
import logging
import json

from igwn_alert import client, DEFAULT_SERVER, DEFAULT_GROUP


def parser():
    parser = argparse.ArgumentParser(prog='igwn-alert')
    parser.add_argument('-g', '--group', default=DEFAULT_GROUP,
                        help='GraceDB group name (e.g., gracedb, '
                             'gracedb-playground)')
    parser.add_argument('-l', '--log', help='Log level', default='error',
                        choices='critical error warning info debug'.split())
    parser.add_argument('-n', '--netrc',
                        help='netrc file (default: read from NETRC '
                        'environment variable or ~/.netrc)')
    parser.add_argument('-s', '--server', default=DEFAULT_SERVER,
                        help='igwn-alert server hostname')
    parser.add_argument('-u', '--username',
                        help='User name (default: look up in auth.toml '
                              'or .netrc)')

    subparsers = parser.add_subparsers(dest='action', help='sub-command help')
    subparsers.required = True

    subparser = subparsers.add_parser(
        'listen', help='Listen for igwn-alert messages and print '
                       'them to stdout.')
    subparser.add_argument(
        'topics', nargs='*', help='a pubsub topic or list of topics '
                                  '(e.g. cbc_gstlal)')

    subparser = subparsers.add_parser(
        'subscriptions', help='List your subscriptions')

    subparser = subparsers.add_parser(
        'topics', help='List available pubsub topics')

    subparser = subparsers.add_parser(
        'unsubscribe', help='Unsubscribe from one or more topics')

    subparser = subparsers.add_parser(
        'send', help='publish contents of a file to a pubsub topic')
    subparser.add_argument(
        'topic', nargs='+', help='a pubsub topic (e.g. cbc_gstlal)')
    subparser.add_argument(
        'alertfile', nargs='+', help='name of the file with the alert to send',
        type=argparse.FileType('rb'))
    return parser


def main(args=None):
    opts = parser().parse_args(args)

    if opts.log is not None:
        logging.basicConfig(level=opts.log.upper())

    lv = client(server=opts.server,
                group=opts.group)

    try:
        if opts.action == 'listen':
            lv.listen(callback=None, topic=[*opts.topics])
        if opts.action == 'topics':
            print("Topics for group {0} associated with the current "
                  "credential:".format(opts.group))
            print(*lv.get_topics(), sep='\n')
        elif opts.action == 'subscriptions':
            raise DeprecationWarning('This feature is deprecated. '
                                     'Please refer to the get_topics() API '
                                     'command or the SCIMMA auth interface.')
        elif opts.action == 'subscribe':
            raise DeprecationWarning('This feature is deprecated. '
                                     'Please refer to the listen() API '
                                     'command or "listen" CLI command.')
        elif opts.action == 'unsubscribe':
            raise DeprecationWarning('This feature is deprecated.')
        elif opts.action == 'send':
            for openfile in opts.alertfile:
                eventfile = openfile.read().decode('utf-8')
                try:
                    alert = json.dumps(eventfile)
                except Exception:
                    alert = eventfile
                lv.publish(topic=opts.topic, msg=alert)
                openfile.close()
    except (KeyboardInterrupt, SystemExit):
        pass
