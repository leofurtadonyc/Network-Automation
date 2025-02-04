#!/usr/bin/env python3
import argparse
import ipaddress
import re
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parse BGP neighbor output and summarize advertised prefixes."
    )
    parser.add_argument("--input", required=True,
                        help="Input file containing the BGP output (any extension)")
    parser.add_argument("--output",
                        help="Optional output file to write the results")
    # Exactly one of --4 or --6 must be specified.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--4", dest="ipv4", action="store_true",
                       help="Process IPv4 prefixes")
    group.add_argument("--6", dest="ipv6", action="store_true",
                       help="Process IPv6 prefixes")
    parser.add_argument("--agg", type=int,
                        help=("Optional custom aggregation prefix length. "
                              "For example, --agg 24 will aggregate into /24s. "
                              "If not provided, for IPv4 the defaults are /8, /16, and /19."))
    return parser.parse_args()

def extract_prefixes(file_content, ip_version):
    """
    Given the file content and desired IP version (4 or 6), extract
    all IP network prefixes that look like A.B.C.D/XX or (for IPv6) like X:X::X/XX.
    """
    prefixes = []
    if ip_version == 4:
        # Matches IPv4 networks like 10.1.0.0/19
        pattern = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3}/\d{1,2})')
    else:
        # A simple (nonexhaustive) pattern for IPv6 prefixes.
        pattern = re.compile(r'([0-9a-fA-F:]+/\d{1,3})')
    for line in file_content.splitlines():
        for match in pattern.finditer(line):
            candidate = match.group(1)
            try:
                net = ipaddress.ip_network(candidate, strict=False)
                if net.version == ip_version:
                    prefixes.append(net)
            except ValueError:
                continue  # Skip invalid network strings.
    return prefixes

def aggregate_prefixes(prefixes, agg_length):
    """
    Given a list of ipaddress.ip_network objects and a desired aggregation prefix length,
    return a sorted list of unique aggregate networks.
    
    For each network:
      - If the route is already as specific as (or more specific than) the agg_length,
        compute the aggregate network that contains it.
      - If the route is broader than the desired aggregation length, split it
        into a list of subnets at the agg_length.
    """
    aggregated_set = set()
    for net in prefixes:
        # If the original route is more specific than or equal to the aggregation length,
        # then simply find the aggregate block that contains the network.
        if net.prefixlen >= agg_length:
            agg_net = ipaddress.ip_network((net.network_address, agg_length), strict=False)
            aggregated_set.add(agg_net)
        else:
            # When the route is broader than the desired agg length, split it into multiple
            # subnets of size /agg_length.
            try:
                for subnet in net.subnets(new_prefix=agg_length):
                    aggregated_set.add(subnet)
            except ValueError:
                # Fallback if subnetting fails for any reason.
                agg_net = ipaddress.ip_network((net.network_address, agg_length), strict=False)
                aggregated_set.add(agg_net)
    # Return the aggregates sorted by their network address.
    return sorted(aggregated_set, key=lambda n: int(n.network_address))

def main():
    args = parse_arguments()

    # Read the input file.
    try:
        with open(args.input, 'r') as f:
            file_content = f.read()
    except IOError as e:
        sys.exit(f"Error reading input file: {e}")

    # Determine which IP version to work with.
    ip_version = 4 if args.ipv4 else 6

    # Extract prefixes from the file.
    prefixes = extract_prefixes(file_content, ip_version)
    if not prefixes:
        sys.exit(f"No valid IPv{ip_version} prefixes found in the input file.")

    # Determine which aggregation levels to use.
    # If the custom aggregation (--agg) is provided, only use that value.
    if args.agg:
        agg_levels = [args.agg]
    else:
        if ip_version == 4:
            agg_levels = [8, 16, 19]
        else:
            # Defaults for IPv6 (adjust these defaults as needed).
            agg_levels = [32, 48, 64]

    output_lines = []
    output_lines.append(f"Total input prefixes: {len(prefixes)}")

    # For each aggregation level, generate aggregates and compute a simple suppression count.
    # Here we use: suppressed = (original prefixes count) - (unique aggregates count)
    # (This is one way to indicate how many routes were “compressed” by aggregation.)
    for agg in agg_levels:
        aggregated = aggregate_prefixes(prefixes, agg)
        suppressed = len(prefixes) - len(aggregated)
        output_lines.append(f"\nAggregation for /{agg}:")
        output_lines.append(f"  Aggregated prefixes count: {len(aggregated)}")
        output_lines.append(f"  Suppressed prefixes count: {suppressed}")
        output_lines.append("  Aggregates:")
        for net in aggregated:
            output_lines.append(f"    {net.with_prefixlen}")
    output_text = "\n".join(output_lines)

    # Display the results.
    print(output_text)

    # If an output file is specified, write the results there.
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_text)
        except IOError as e:
            sys.exit(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
