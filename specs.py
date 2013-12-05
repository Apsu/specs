#!/usr/bin/python2

from __future__ import print_function
from dateutil import parser

import datetime
import pyrax

# Set some useful things
diff = datetime.timedelta(weeks=2)
now = datetime.datetime.utcnow()
servers = {}
usage = {}
regions = ['DFW', 'ORD', 'IAD', 'SYD', 'HKG']

pyrax.set_setting('identity_type', 'rackspace') # Set identity type

print("It is now: {0}.".format(now.ctime()))
print("Matching only instances created >= {0} days ago.".format(diff.days))
print("Authenticating...")
pyrax.set_credential_file('creds') # Load credentials file

print("Fetching information and filtering...")
for region in regions:
    cs = pyrax.connect_to_cloudservers(region=region)
    flavors = dict((str(flavor.id), flavor) for flavor in cs.flavors.list())
    usage[region] = {'ram': 0, 'disk': 0, 'vcpus': 0}
    servers[region] = []
    for server in cs.list():
        dt = parser.parse(server.created, ignoretz=True)
        if dt + diff < now:
            flavor = flavors[server.flavor['id']]
            usage[region]['ram'] += flavor.ram
            usage[region]['disk'] += flavor.disk
            usage[region]['vcpus'] += flavor.vcpus
            servers[region].append(
                {'name': server.name, 'flavor': flavor, 'created': dt}
            )

width=8 # Most fields are short
fwidth=max(
    [len(server['flavor'].id) for region in regions
     for server in servers[region]]
) # Figure out longest flavor name
nwidth=max(
    [len(server['name']) for region in regions
     for server in servers[region]]
) # Figure out longest server name

print()
print("Instance details by region, then date:")
print("{0:{width}} {1:{nwidth}} {2:{fwidth}} "
      "{3:{width}} {4:{width}} {5:{width}} {6}".format(
          'Region', 'Name', 'Flavor', 'RAM', 'Disk', 'VCPUs', 'Creation Time',
          width=width, fwidth=fwidth, nwidth=nwidth
      )
)

for region in regions:
    from operator import itemgetter
    for server in sorted(servers[region], key=itemgetter('created')):
        print("{0:{width}} {1:{nwidth}} {2:{fwidth}} "
              "{3:{width}} {4:{width}} {5:{width}} {6}".format(
                  region, server['name'], server['flavor'].id,
                  str(server['flavor'].ram), str(server['flavor'].disk),
                  str(server['flavor'].vcpus), server['created'].ctime(),
                  width=width, fwidth=fwidth, nwidth=nwidth
              )
        )

print()
print("Total usage by region:")
print("{0:{width}} {1:{width}} {2:{width}} {3:{width}} {4:{width}}".format(
    'Region', 'VMs', 'RAM', 'Disk', 'VCPUs', width=width)
)
for region in regions:
    print("{0:{width}} {1:{width}} {2:{width}} {3:{width}} {4:{width}}".format(
        region, str(len(servers[region])), str(usage[region]['ram']),
        str(usage[region]['disk']), str(usage[region]['vcpus']), width=width)
    )
