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
    # Allow multiple aggregation levels, e.g., --agg 19 --agg 20 --agg 21.
    parser.add_argument("--agg", type=int, action="append",
                        help=("Optional custom aggregation prefix length(s). "
                              "For example, --agg 19 --agg 20 --agg 21. "
                              "If not provided, for IPv4 the defaults are /8, /16, and /19."))
    return parser.parse_args()

def extract_prefixes(file_content, ip_version):
    """
    Extract any IPv4 or IPv6 network/prefix strings found in the file content.
    (This regex is broad and might pick up extra strings, so you may wish to refine it.)
    """
    prefixes = []
    if ip_version == 4:
        # Matches IPv4 addresses like 10.1.0.0/19.
        pattern = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3}/\d{1,2})')
    else:
        # A basic (nonexhaustive) pattern for IPv6 prefixes.
        pattern = re.compile(r'([0-9a-fA-F:]+/\d{1,3})')
    for line in file_content.splitlines():
        for match in pattern.finditer(line):
            candidate = match.group(1)
            try:
                net = ipaddress.ip_network(candidate, strict=False)
                if net.version == ip_version:
                    prefixes.append(net)
            except ValueError:
                continue
    return prefixes

def aggregate_prefixes(prefixes, agg_length):
    """
    Group input prefixes into aggregate blocks defined by agg_length.
    Only prefixes that are as specific as (or more specific than) the agg_length are eligible.
    An aggregate is produced only when a given block contains more than one eligible prefix.
    
    Returns three values:
      aggregates: a sorted list of aggregate networks (only groups with > 1 prefix).
      suppressed_count: total count of suppressed prefixes (for each aggregated group, count = group size - 1).
      not_aggregated_count: count of prefixes not aggregated because they either:
          - have a prefix length less than the aggregation target (too broad), or
          - are alone in their aggregate group (i.e. no more specific “siblings”)
    """
    groups = {}  # key: aggregate network (e.g. 10.1.0.0/20), value: list of matching prefixes
    broad_prefixes = []  # prefixes that are too broad (prefixlen < agg_length)
    
    for net in prefixes:
        if net.prefixlen < agg_length:
            broad_prefixes.append(net)
        else:
            # Compute the aggregate block that this prefix falls into.
            agg_net = ipaddress.ip_network((net.network_address, agg_length), strict=False)
            groups.setdefault(agg_net, []).append(net)
    
    aggregates = []
    suppressed_count = 0
    # Start not_aggregated_count with the prefixes that are too broad.
    not_aggregated_count = len(broad_prefixes)
    
    # Process groups that are eligible (i.e. prefixes with prefixlen >= agg_length)
    for agg_net, nets in groups.items():
        if len(nets) > 1:
            aggregates.append(agg_net)
            suppressed_count += (len(nets) - 1)
        else:
            # A group with only one prefix is not aggregated.
            not_aggregated_count += 1
    
    # Return the aggregates sorted by network address.
    aggregates = sorted(aggregates, key=lambda n: int(n.network_address))
    return aggregates, suppressed_count, not_aggregated_count

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
    prefixes = extract_prefixes(file_content, ip_version)
    if not prefixes:
        sys.exit(f"No valid IPv{ip_version} prefixes found in the input file.")

    # Determine which aggregation levels to use.
    if args.agg:
        agg_levels = args.agg
    else:
        if ip_version == 4:
            agg_levels = [8, 16, 19]
        else:
            agg_levels = [32, 48, 64]

    total_input = len(prefixes)
    output_lines = []
    output_lines.append(f"Total input prefixes: {total_input}")

    # Process each specified aggregation level.
    for agg in agg_levels:
        aggregates, suppressed_count, not_aggregated_count = aggregate_prefixes(prefixes, agg)
        output_lines.append(f"\nAggregation for /{agg}:")
        output_lines.append(f"  Aggregated prefixes count: {len(aggregates)}")
        output_lines.append(f"  Suppressed prefixes count: {suppressed_count}")
        output_lines.append(f"  Not aggregated prefixes count (prefix length less than /{agg} or singletons): {not_aggregated_count}")
        total_output = len(aggregates) + not_aggregated_count
        savings_percentage = (suppressed_count / total_input * 100) if total_input else 0
        output_lines.append(f"  Summary: Total input prefixes: {total_input}, Total output prefixes (Aggregated + Not Aggregated): {total_output}, Suppressed prefixes: {suppressed_count}, Savings: {savings_percentage:.2f}%")
        if aggregates:
            output_lines.append("  Aggregates:")
            for net in aggregates:
                output_lines.append(f"    {net.with_prefixlen}")
        else:
            output_lines.append("  No aggregates produced for this aggregation level.")
    
    output_text = "\n".join(output_lines)
    print(output_text)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_text)
        except IOError as e:
            sys.exit(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
