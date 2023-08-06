This project follows [Semantic Versioning](https://semver.org/).

> Notice: Major version zero (0.y.z) is for initial development. Anything MAY change at any time. This public API SHOULD NOT be considered stable.

## 0.1.2

* Fix PeeringDB Authentication!
    * See the [relevant GitHub Issue](https://github.com/peeringdb/peeringdb/issues/1206#issuecomment-1202550667) where we discovered the following details about PeeringDB API Basic Authentication:
    > 1. Do NOT base64 encode
    > 2. Username/Password Must be space-separated (e.g., must not be colon ":" separated)
    > 3. Username when using API tokens is "Api-Key"
    > 4. Ensure "www" is in all API requests!
* Enable using PeeringDB API Key instead of username/password.
    * Exposed via `--peeringdb-key` argument in `routeviews-build-peer` CLI tool (or as env var: `PEERINGDB_KEY`).
* Add the filepath to the exception message when `routeviews.yaml` encounters a `ParseError`.
    * This enables fixing syntax issues very quickly.
    * "Unable to parse `<filepath>`" is the added message, seen below:
    ```
    ... omitted traceback for brevity...
    routeviews.yaml.ParseError: while parsing a block mapping
        in "<unicode string>", line 1, column 1:
            short_name: decix
            ^ (line: 1)
    expected <block end>, but found '-'
        in "<unicode string>", line 109, column 1:
            - peer_as: 8888
            ^ (line: 109)
    Unable to parse <working-tree>/ansible/inventory/host_vars/route-views.decix.routeviews.org
    ```
* Ensure that PyVCR cassettes do not contain HTTP Basic Authentication secrets.
    * Rotated the (randomly generated) Base64 encoded password that was previously exposed via HTTP Basic Authentication Headers. 

## 0.1.1

* Fix Bug: Package failed to declare some critical dependencies. 


## 0.1.0

> Bug: Package failed to declare some critical dependencies. 
> Was missing `uologging` and `raumel.yaml` dependencies deceleration in "setup.py".

The first release of the routeviews package contains some core CLI tools, as well as some functions/classes that might be useful to routeviews maintainers.

### CLI Tools

Provide two CLI tools:

* [`routeviews-build-peer` CLI tool](./user-guide.md#routeviews-build-peer-cli-tool): automation of updating ["Route Views Ansible inventory"](https://github.com/routeviews/infra), toward 'adding BGP peers to XYZ collectors'.
* [`routeviews-email-peers` CLI tool](./user-guide.md#routeviews-email-peers-cli-tool): get list of email addresses actively peered with a Route Views Collector.

### Libraries

* There is the `routeviews.peeringdb` package that has some great methods for interfacing with the PeeringDB API.
* There is the `routeviews.yaml` module that can load and save YAML config files (without rearranging them).
    * Depends on the [`ruamel.yaml` package](https://pypi.org/project/ruamel.yaml/)
* There is the `routeviews.ansible` package, that can load, modify, and save the Route Views Ansible Inventory.
* There is the `routeviews.bgpsummery` module, that defines a `BGPSummary` class as well as functions for retrieving a `BGPSummary` from any collector.
* There is the (start of a) `routeviews.api` module/package, for interfacing with the Route Views API/DB (undocumented).



