Route Views requires many tools to support its functionality.
This package is a place for those tools to live.

This package also acts as a python library for Route Views.

## `routeviews-build-peer` CLI tool

This tool is for (consistently) updating the [Route Views ansible inventory (private repo)](https://github.com/routeviews/infra) when folks submit new peer requests. 

> This tool uses information provided by PeeringDB for the peering information.

### Prerequisites

1. *Route Views Ansible Inventory*: You must have a local copy of the Route Views ansible inventory available, for this tool to update.
    * If you will be running this command with any regularity, is useful to export the `ROUTEVIEWS_INVENTORY` environment variable to point to your local copy of the [Route Views ansible inventory repository (private)](https://github.com/routeviews/infra).
    ```
    # (Optional) Place in your ~/.bashrc
    export ROUTEVIEWS_INVENTORY='<working-tree>/ansible/inventory'
    ```
    * `<working-tree>` refers to wherever you've cloned the repository on your filesystem.

### Example: Peer with an ASN using IP Addresses

This tool supports arguments for `asn`, as well as `ip`.
The `ip` argument can be used multiple times to peer with multiple IP Addresses at once.

> ⚠ Only supports peering with one ASN at a time.

> ℹ Use the `--help` flag to learn more about how to use these arguments.

As discussed in the [prerequisites](#prerequisites-1), there is also the `inventory` argument required that points to the "inventory/" directory.

> ℹ Tip: Provide an `asn` and omit the `ip` argument entirely -- the tool will attempt to peer with ALL compatible IP Addresses for the provided `asn`!

    routeviews-build-peer \
        --inventory <working-tree>/ansible/inventory \
        --asn 15169 \
        --ip 202.249.2.189 \
        --ip 2001:200:0:fe00::3b41:0 \
        --ip 80.249.208.247 \
        --ip 2001:7f8:1::a501:5169:1 
    Changes:

    Diff of "<working-tree>/ansible/inventory/host_vars/route-views.amsix.routeviews.org"
    + peer_as: 15169
    + peer_address: 80.249.208.247
    + description: AMS-IX
    + afi_safis:
    +   - ipv4_unicast
    + peer_as: 15169
    + peer_address: 2001:7f8:1::a501:5169:1
    + description: AMS-IX
    + afi_safis:
    +   - ipv6_unicast

    Diff of "<working-tree>/ansible/inventory/host_vars/route-views.wide.routeviews.org"
    + peer_as: 15169
    + peer_address: 202.249.2.189
    + description: DIX-IE
    + afi_safis:
    +   - ipv4_unicast
    + peer_as: 15169
    + peer_address: 2001:200:0:fe00::3b41:0
    + description: DIX-IE
    + afi_safis:
    +   - ipv6_unicast

### Example: Peer with an ASN (at ALL IXes)

If an ASN is wanting to connect wherever possible, provide only the `asn` argument and the tool will determine all the possible `ip` arguments from PeeringDB.

    routeviews-build-peer \
        --inventory <working-tree>/ansible/inventory \
        --asn 15169
    
    Changes:

    Diff of "/home12/rleonar7/routeviews/infra/ansible/inventory/host_vars/route-views.perth.routeviews.org"
    + peer_as: 15169
    + peer_address: 218.100.52.3
    + description: 'IX Australia (Sydney NSW): NSW-IX'
    + afi_safis:
    +   - ipv4_unicast
    + peer_as: 15169
    + peer_address: 2001:7fa:11:4:0:3b41:0:1
    + description: 'IX Australia (Sydney NSW): NSW-IX'
    + afi_safis:
    +   - ipv6_unicast
    + peer_as: 15169
    + peer_address: 218.100.53.29
    + description: 'IX Australia (Sydney NSW): NSW-IX'
    + afi_safis:
    +   - ipv4_unicast
    + peer_as: 15169
    + peer_address: 2001:7fa:11:4:0:3b41:0:2
    + description: 'IX Australia (Sydney NSW): NSW-IX'
    + afi_safis:
    +   - ipv6_unicast
    + peer_as: 15169
    + peer_address: 218.100.78.154
    + description: 'IX Australia (Melbourne VIC): VIC-IX'
    + afi_safis:
    +   - ipv4_unicast
    + peer_as: 15169
    + peer_address: 2001:7fa:11:1:0:3b41:0:2
    + description: 'IX Australia (Melbourne VIC): VIC-IX'
    + afi_safis:
    +   - ipv6_unicast
    + peer_as: 15169
    + peer_address: 218.100.78.153
    + description: 'IX Australia (Melbourne VIC): VIC-IX'
    + afi_safis:
    +   - ipv4_unicast
    + peer_as: 15169
    + peer_address: 2001:7fa:11:1:0:3b41:0:1
    + description: 'IX Australia (Melbourne VIC): VIC-IX'
    + afi_safis:
    +   - ipv6_unicast

    Diff of "/home12/rleonar7/routeviews/infra/ansible/inventory/host_vars/route-views.amsix.routeviews.org"
    + peer_as: 15169
    + peer_address: 80.249.208.247
    + description: AMS-IX
    + afi_safis:
    +   - ipv4_unicast
    + peer_as: 15169
    + peer_address: 2001:7f8:1::a501:5169:1
    + description: AMS-IX
    + afi_safis:
    ... trimmed for brevity...

## `routeviews-email-peers` CLI tool

This tool will get a list of email addresses for any networks that are actively peered with a particular Route Views Collector.
This tool is for gathering email address information about Route Views Collector's peers around the world, leveraging [PeeringDB]() and [RDAP](TODO).

> Future Plan: Use UO SMTP server to automate actually sending *many* types of 'standard Route Views Operations emails' (use Jinja2 Templates for the email templates).

### Prerequisites

1. *SSH Access*: This script uses NetMiko, and assumes that the current user can SSH into the collector using SSH keys (recommend using an `ssh-agent`).
2. *PeeringDB Account (Optional, if you would like this tool to search PeeringDB)*: Export your PeeringDB credentials as environment variables, `PEERINGDB_USERNAME` and `PEERINGDB_PASSWORD`:
    ```
    # (Optional) Place in your ~/.bashrc
    export PEERINGDB_USERNAME=rleonar7
    export PEERINGDB_PASSWORD=MySuperSecretPassword
    ```
> (non)Anonymous access to PeeringDB API: Unfortunately, PeeringDB APIs only return the info we need when using a PeeringDB account, and not when using anonymous access.

### Example

Run the `routeviews-email-peers` command against a specific Route Views collector, e.g. "route-views4.routeviews.org".

Today, this command will to produce a semicolon-separated list of email addresses for each (established) peering session on that collector.

    $ routeviews-email-peers --collector route-views4.routeviews.org
    > WARNING:root:No email found for ASN: 204028
    > noc@netactuate.com; noc@enetworks.co.za; noc@net.internet2.edu; ... trimmed for brevity...

## YAML Python API

We have a custom YAML module for handling (Ansible) YAML config files.
In particular, this module will handle whitespace matching the standard way used throughout the Route Views Infrastructure repo.
Further, this module ensures that the order data dumped is the same as ingested.

> Today, this functionality comes thanks to the [ruamel.yaml package (PyPI)](https://pypi.org/project/ruamel.yaml/)!

### Example

This example loads a file by filename, then saves that file back.

> In this case, this will essentially create a copy the "vars.yml" file.
>
> ℹ Tip: The "vars2.yml" copy, or any file dumped using `routeviews.yaml`, will follow the Route Views YAML styling convention.

    import routeviews.yaml

    my_variables = routeviews.yaml.load('vars.yml')

    # ... make updates to `my_variables`...

    routeviews.yaml.dump(my_variables, 'vars2.yml')

## Additional APIs

Besides the CLI tools discussed above, this package contains many internal packages/modules that might be useful.

> ⚠ NOTICE: Major version zero (0.y.z) is for initial development. Anything MAY change at any time. This public API SHOULD NOT be considered stable.

* There is the `routeviews.peeringdb` package that has some great methods for interfacing with the PeeringDB API.
* There is the `routeviews.yaml` module that can load and save YAML config files (without rearranging them).
    * Depends on the [`ruamel.yaml` package](https://pypi.org/project/ruamel.yaml/)
* There is the `routeviews.ansible` package, that can load, modify, and save the Route Views Ansible Inventory.
* There is the `routeviews.bgpsummery` module, that defines a `BGPSummary` class as well as functions for retrieving a `BGPSummary` from any collector.
* There is the (start of a) `routeviews.api` module/package, for interfacing with the Route Views API/DB (undocumented).






