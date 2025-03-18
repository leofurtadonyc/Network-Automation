
set interfaces lo0 unit 0 family inet filter input-list ACCEPT_COMMOM_SERVICES
set interfaces lo0 unit 0 family inet filter input-list ACCEPT_IGP
set interfaces lo0 unit 0 family inet filter input-list ACCEPT_LDP_RSVP
set interfaces lo0 unit 0 family inet filter input-list ACCEPT_BGP
set interfaces lo0 unit 0 family inet filter input-list ACCEPT_BGP_SERVICES
set interfaces lo0 unit 0 family inet filter input-list ACCEPT_REMOTE_AUTH
set interfaces lo0 unit 0 family inet filter input-list ACCEPT_MULTICAST



lfurtado@CORE_BRE_JUNOS> show configuration firewall | display set    
set firewall family inet prefix-action management-police-set policer management-1m
set firewall family inet prefix-action management-police-set count
set firewall family inet prefix-action management-police-set filter-specific
set firewall family inet prefix-action management-police-set subnet-prefix-length 64
set firewall family inet prefix-action management-police-set destination-prefix-length 128
set firewall family inet prefix-action management-high-police-set apply-flags omit
set firewall family inet prefix-action management-high-police-set policer management-5m
set firewall family inet prefix-action management-high-police-set count
set firewall family inet prefix-action management-high-police-set filter-specific
set firewall family inet prefix-action management-high-police-set subnet-prefix-length 64
set firewall family inet prefix-action management-high-police-set destination-prefix-length 128
set firewall family inet filter ACCEPT_COMMOM_SERVICES apply-flags omit
set firewall family inet filter ACCEPT_COMMOM_SERVICES term ACCEPT_ICMP filter ACCEPT_ICMP
set firewall family inet filter ACCEPT_COMMOM_SERVICES term ACCEPT_TRACEROUTE filter ACCEPT_TRACEROUTE
set firewall family inet filter ACCEPT_COMMOM_SERVICES term ACCEPT_SSH filter ACCEPT_SSH
set firewall family inet filter ACCEPT_COMMOM_SERVICES term ACCEPT_SNMP filter ACCEPT_SNMP
set firewall family inet filter ACCEPT_COMMOM_SERVICES term ACCEPT_NTP filter ACCEPT_NTP
set firewall family inet filter ACCEPT_COMMOM_SERVICES term ACCEPT_WEB filter ACCEPT_WEB
set firewall family inet filter ACCEPT_COMMOM_SERVICES term ACCEPT_DNS filter ACCEPT_DNS
set firewall family inet filter ACCEPT_COMMOM_SERVICES term ACCEPT_FTP filter ACCEPT_FTP
set firewall family inet filter ACCEPT_REMOTE_AUTH apply-flags omit
set firewall family inet filter ACCEPT_REMOTE_AUTH term ACCEPT_RADIUS filter ACCEPT_RADIUS
set firewall family inet filter ACCEPT_REMOTE_AUTH term accept-tacas filter ACCEPT_TACACS
set firewall family inet filter ACCEPT_IGP apply-flags omit
set firewall family inet filter ACCEPT_IGP term ACCEPT_OSPF filter ACCEPT_OSPF
set firewall family inet filter ACCEPT_LDP_RSVP apply-flags omit
set firewall family inet filter ACCEPT_LDP_RSVP term ACCEPT_LDP filter ACCEPT_LDP
set firewall family inet filter ACCEPT_LDP_RSVP term ACCEPT_RSVP filter ACCEPT_RSVP
set firewall family inet filter ACCEPT_BGP apply-flags omit
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP from source-prefix-list bgp-neighbors-ipv6
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP from source-prefix-list bgp-neighbors-logical-systems-ipv6
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP from destination-prefix-list router-ipv6
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP from destination-prefix-list router-ipv6-logical-systems
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP from destination-prefix-list router-irb-ipv6
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP from protocol tcp
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP from port bgp
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP then count ACCEPT_BGP
set firewall family inet filter ACCEPT_BGP term ACCEPT_BGP then accept
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-rtr from source-address 177.129.8.0/24
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-rtr from source-address 10.3.0.0/24
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-rtr from protocol tcp
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-rtr from port 3323
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-rtr then count accept-rtr
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-rtr then accept
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-bmp from source-address 177.129.8.0/24
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-bmp from protocol tcp
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-bmp from port 5000
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-bmp then count accept-snas
set firewall family inet filter ACCEPT_BGP_SERVICES term accept-bmp then accept
set firewall family inet filter ACCEPT_ICMP apply-flags omit
set firewall family inet filter ACCEPT_ICMP term no-icmp-fragments from is-fragment
set firewall family inet filter ACCEPT_ICMP term no-icmp-fragments from protocol icmp
set firewall family inet filter ACCEPT_ICMP term no-icmp-fragments then count no-icmp-fragments
set firewall family inet filter ACCEPT_ICMP term no-icmp-fragments then log
set firewall family inet filter ACCEPT_ICMP term no-icmp-fragments then discard
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from protocol icmp
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from ttl-except 1
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from icmp-type echo-reply
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from icmp-type echo-request
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from icmp-type time-exceeded
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from icmp-type unreachable
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from icmp-type router-advertisement
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from icmp-type parameter-problem
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP from icmp-type source-quench
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP then policer management-5m
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP then count ACCEPT_ICMP
set firewall family inet filter ACCEPT_ICMP term ACCEPT_ICMP then accept
set firewall family inet filter ACCEPT_TRACEROUTE apply-flags omit
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-udp from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-udp from protocol udp
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-udp from ttl 1
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-udp from destination-port 33435-33450
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-udp then policer management-1m
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-udp then count accept-traceroute-udp
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-udp then accept
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp from protocol icmp
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp from ttl 1
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp from icmp-type echo-request
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp from icmp-type timestamp
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp from icmp-type time-exceeded
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp then policer management-1m
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp then count accept-traceroute-icmp
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-icmp then accept
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-tcp from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-tcp from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-tcp from protocol tcp
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-tcp from ttl 1
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-tcp then policer management-1m
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-tcp then count accept-traceroute-tcp
set firewall family inet filter ACCEPT_TRACEROUTE term accept-traceroute-tcp then accept
set firewall family inet filter ACCEPT_SSH apply-flags omit
set firewall family inet filter ACCEPT_SSH term ACCEPT_SSH from source-prefix-list mgmt-prefixes
set firewall family inet filter ACCEPT_SSH term ACCEPT_SSH from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_SSH term ACCEPT_SSH from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_SSH term ACCEPT_SSH from protocol tcp
set firewall family inet filter ACCEPT_SSH term ACCEPT_SSH from destination-port ssh
set firewall family inet filter ACCEPT_SSH term ACCEPT_SSH then policer management-5m
set firewall family inet filter ACCEPT_SSH term ACCEPT_SSH then count ACCEPT_SSH
set firewall family inet filter ACCEPT_SSH term ACCEPT_SSH then accept
set firewall family inet filter ACCEPT_SNMP apply-flags omit
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP from source-prefix-list snmp-client-lists
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP from source-prefix-list snmp-community-clients
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP from protocol udp
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP from destination-port snmp
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP then policer management-5m
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP then count ACCEPT_SNMP
set firewall family inet filter ACCEPT_SNMP term ACCEPT_SNMP then accept
set firewall family inet filter ACCEPT_NTP apply-flags omit
set firewall family inet filter ACCEPT_NTP term ACCEPT_NTP from source-prefix-list ntp-server
set firewall family inet filter ACCEPT_NTP term ACCEPT_NTP from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_NTP term ACCEPT_NTP from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_NTP term ACCEPT_NTP from protocol udp
set firewall family inet filter ACCEPT_NTP term ACCEPT_NTP from port ntp
set firewall family inet filter ACCEPT_NTP term ACCEPT_NTP then policer management-1m
set firewall family inet filter ACCEPT_NTP term ACCEPT_NTP then count ACCEPT_NTP
set firewall family inet filter ACCEPT_NTP term ACCEPT_NTP then accept
set firewall family inet filter ACCEPT_NTP term accept-ntp-peer from source-prefix-list ntp-server-peers
set firewall family inet filter ACCEPT_NTP term accept-ntp-peer from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_NTP term accept-ntp-peer from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_NTP term accept-ntp-peer from protocol udp
set firewall family inet filter ACCEPT_NTP term accept-ntp-peer from destination-port ntp
set firewall family inet filter ACCEPT_NTP term accept-ntp-peer then policer management-1m
set firewall family inet filter ACCEPT_NTP term accept-ntp-peer then count accept-ntp-peer
set firewall family inet filter ACCEPT_NTP term accept-ntp-peer then accept
set firewall family inet filter ACCEPT_NTP term accept-ntp-server from source-prefix-list mgmt-prefixes
set firewall family inet filter ACCEPT_NTP term accept-ntp-server from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_NTP term accept-ntp-server from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_NTP term accept-ntp-server from protocol udp
set firewall family inet filter ACCEPT_NTP term accept-ntp-server from destination-port ntp
set firewall family inet filter ACCEPT_NTP term accept-ntp-server then policer management-1m
set firewall family inet filter ACCEPT_NTP term accept-ntp-server then count accept-ntp-server
set firewall family inet filter ACCEPT_NTP term accept-ntp-server then accept
set firewall family inet filter ACCEPT_RADIUS apply-flags omit
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS from source-prefix-list radius-servers
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS from protocol udp
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS from source-port radacct
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS from source-port radius
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS from tcp-established
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS then policer management-1m
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS then count ACCEPT_RADIUS
set firewall family inet filter ACCEPT_RADIUS term ACCEPT_RADIUS then accept
set firewall family inet filter ACCEPT_TACACS apply-flags omit
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS from source-prefix-list tacacs-servers
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS from protocol tcp
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS from protocol udp
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS from source-port tacacs
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS from source-port tacacs-ds
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS from tcp-established
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS then policer management-1m
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS then count ACCEPT_TACACS
set firewall family inet filter ACCEPT_TACACS term ACCEPT_TACACS then accept
set firewall family inet filter ACCEPT_OSPF apply-flags omit
set firewall family inet filter ACCEPT_OSPF term ACCEPT_OSPF from source-prefix-list router-ipv4
set firewall family inet filter ACCEPT_OSPF term ACCEPT_OSPF from source-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_OSPF term ACCEPT_OSPF from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_OSPF term ACCEPT_OSPF from destination-prefix-list ospf
set firewall family inet filter ACCEPT_OSPF term ACCEPT_OSPF from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_OSPF term ACCEPT_OSPF from protocol ospf
set firewall family inet filter ACCEPT_OSPF term ACCEPT_OSPF then count ACCEPT_OSPF
set firewall family inet filter ACCEPT_OSPF term ACCEPT_OSPF then accept
set firewall family inet filter ACCEPT_LDP apply-flags omit
set firewall family inet filter ACCEPT_LDP term accept-ldp-discover from source-prefix-list router-ipv4
set firewall family inet filter ACCEPT_LDP term accept-ldp-discover from source-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_LDP term accept-ldp-discover from source-prefix-list backbone-prefix-list
set firewall family inet filter ACCEPT_LDP term accept-ldp-discover from destination-prefix-list multicast-all-routers
set firewall family inet filter ACCEPT_LDP term accept-ldp-discover from protocol udp
set firewall family inet filter ACCEPT_LDP term accept-ldp-discover from destination-port ldp
set firewall family inet filter ACCEPT_LDP term accept-ldp-discover then count accept-ldp-discover
set firewall family inet filter ACCEPT_LDP term accept-ldp-discover then accept
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast from source-prefix-list router-ipv4
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast from source-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast from source-prefix-list backbone-prefix-list
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast from protocol tcp
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast from port ldp
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast then count accept-ldp-unicast
set firewall family inet filter ACCEPT_LDP term accept-ldp-unicast then accept
set firewall family inet filter ACCEPT_LDP term accept-tldp-discover from source-prefix-list backbone-prefix-list
set firewall family inet filter ACCEPT_LDP term accept-tldp-discover from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_LDP term accept-tldp-discover from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_LDP term accept-tldp-discover from protocol udp
set firewall family inet filter ACCEPT_LDP term accept-tldp-discover from destination-port ldp
set firewall family inet filter ACCEPT_LDP term accept-tldp-discover then count accept-tldp-discover
set firewall family inet filter ACCEPT_LDP term accept-tldp-discover then accept
set firewall family inet filter ACCEPT_LDP term accept-ldp-igmp from source-prefix-list router-ipv4
set firewall family inet filter ACCEPT_LDP term accept-ldp-igmp from source-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_LDP term accept-ldp-igmp from source-prefix-list backbone-prefix-list
set firewall family inet filter ACCEPT_LDP term accept-ldp-igmp from destination-prefix-list multicast-all-routers
set firewall family inet filter ACCEPT_LDP term accept-ldp-igmp from protocol igmp
set firewall family inet filter ACCEPT_LDP term accept-ldp-igmp then count accept-ldp-igmp
set firewall family inet filter ACCEPT_LDP term accept-ldp-igmp then accept
set firewall family inet filter ACCEPT_RSVP apply-flags omit
set firewall family inet filter ACCEPT_RSVP term ACCEPT_RSVP from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_RSVP term ACCEPT_RSVP from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_RSVP term ACCEPT_RSVP from protocol rsvp
set firewall family inet filter ACCEPT_RSVP term ACCEPT_RSVP then count ACCEPT_RSVP
set firewall family inet filter ACCEPT_RSVP term ACCEPT_RSVP then accept
set firewall family inet filter ACCEPT_BFD apply-flags omit
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD from source-prefix-list router-ipv4
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD from source-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD from protocol udp
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD from source-port 49152-65535
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD from destination-port 3784-3785
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD then count ACCEPT_BFD
set firewall family inet filter ACCEPT_BFD term ACCEPT_BFD then accept
set firewall family inet filter ACCEPT_FTP apply-flags omit
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP from source-address 177.129.8.0/24
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP from protocol tcp
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP from port ftp
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP from port ftp-data
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP then policer management-5m
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP then count ACCEPT_FTP
set firewall family inet filter ACCEPT_FTP term ACCEPT_FTP then accept
set firewall family inet filter ACCEPT_TELNET apply-flags omit
set firewall family inet filter ACCEPT_TELNET term ACCEPT_TELNET from source-prefix-list mgmt-prefixes
set firewall family inet filter ACCEPT_TELNET term ACCEPT_TELNET from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_TELNET term ACCEPT_TELNET from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_TELNET term ACCEPT_TELNET from protocol tcp
set firewall family inet filter ACCEPT_TELNET term ACCEPT_TELNET from destination-port telnet
set firewall family inet filter ACCEPT_TELNET term ACCEPT_TELNET then policer management-1m
set firewall family inet filter ACCEPT_TELNET term ACCEPT_TELNET then count ACCEPT_TELNET
set firewall family inet filter ACCEPT_TELNET term ACCEPT_TELNET then accept
set firewall family inet filter ACCEPT_VRRP apply-flags omit
set firewall family inet filter ACCEPT_VRRP term ACCEPT_VRRP from source-prefix-list router-ipv4
set firewall family inet filter ACCEPT_VRRP term ACCEPT_VRRP from source-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_VRRP term ACCEPT_VRRP from destination-prefix-list vrrp
set firewall family inet filter ACCEPT_VRRP term ACCEPT_VRRP from protocol vrrp
set firewall family inet filter ACCEPT_VRRP term ACCEPT_VRRP from protocol ah
set firewall family inet filter ACCEPT_VRRP term ACCEPT_VRRP then count ACCEPT_VRRP
set firewall family inet filter ACCEPT_VRRP term ACCEPT_VRRP then accept
set firewall family inet filter DISCARD_ALL apply-flags omit
set firewall family inet filter DISCARD_ALL term discard-ip-options from ip-options any
set firewall family inet filter DISCARD_ALL term discard-ip-options then count discard-ip-options
set firewall family inet filter DISCARD_ALL term discard-ip-options then log
set firewall family inet filter DISCARD_ALL term discard-ip-options then syslog
set firewall family inet filter DISCARD_ALL term discard-ip-options then discard
set firewall family inet filter DISCARD_ALL term discard-TTL_1-unknown from ttl 1
set firewall family inet filter DISCARD_ALL term discard-TTL_1-unknown then count discard-all-TTL_1-unknown
set firewall family inet filter DISCARD_ALL term discard-TTL_1-unknown then log
set firewall family inet filter DISCARD_ALL term discard-TTL_1-unknown then syslog
set firewall family inet filter DISCARD_ALL term discard-TTL_1-unknown then discard
set firewall family inet filter DISCARD_ALL term discard-tcp from protocol tcp
set firewall family inet filter DISCARD_ALL term discard-tcp then count discard-tcp
set firewall family inet filter DISCARD_ALL term discard-tcp then log
set firewall family inet filter DISCARD_ALL term discard-tcp then syslog
set firewall family inet filter DISCARD_ALL term discard-tcp then discard
set firewall family inet filter DISCARD_ALL term discard-netbios from protocol udp
set firewall family inet filter DISCARD_ALL term discard-netbios from destination-port 137
set firewall family inet filter DISCARD_ALL term discard-netbios then count discard-netbios
set firewall family inet filter DISCARD_ALL term discard-netbios then log
set firewall family inet filter DISCARD_ALL term discard-netbios then syslog
set firewall family inet filter DISCARD_ALL term discard-netbios then discard
set firewall family inet filter DISCARD_ALL term discard-udp from protocol udp
set firewall family inet filter DISCARD_ALL term discard-udp then count discard-udp
set firewall family inet filter DISCARD_ALL term discard-udp then log
set firewall family inet filter DISCARD_ALL term discard-udp then syslog
set firewall family inet filter DISCARD_ALL term discard-udp then discard
set firewall family inet filter DISCARD_ALL term discard-icmp from protocol icmp
set firewall family inet filter DISCARD_ALL term discard-icmp then count discard-icmp
set firewall family inet filter DISCARD_ALL term discard-icmp then log
set firewall family inet filter DISCARD_ALL term discard-icmp then syslog
set firewall family inet filter DISCARD_ALL term discard-icmp then discard
set firewall family inet filter DISCARD_ALL term discard-unknown then count discard-unknown
set firewall family inet filter DISCARD_ALL term discard-unknown then log
set firewall family inet filter DISCARD_ALL term discard-unknown then syslog
set firewall family inet filter DISCARD_ALL term discard-unknown then discard
set firewall family inet filter ACCEPT_ESTABLIDHED apply-flags omit
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ssh from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ssh from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ssh from source-port ssh
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ssh from tcp-established
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ssh then policer management-5m
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ssh then count accept-established-tcp-ssh
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ssh then accept
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp from source-port ftp
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp from tcp-established
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp then policer management-5m
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp then count accept-established-tcp-ftp
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp then accept
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data-syn from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data-syn from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data-syn from source-port ftp-data
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data-syn from tcp-initial
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data-syn then policer management-5m
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data-syn then count accept-established-tcp-ftp-data-syn
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data-syn then accept
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data from source-port ftp-data
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data from tcp-established
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data then policer management-5m
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data then count accept-established-tcp-ftp-data
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-ftp-data then accept
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-telnet from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-telnet from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-telnet from source-port telnet
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-telnet from tcp-established
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-telnet then policer management-5m
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-telnet then count accept-established-tcp-telnet
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-telnet then accept
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-fetch from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-fetch from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-fetch from source-port http
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-fetch from source-port https
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-fetch from tcp-established
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-fetch then policer management-5m
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-fetch then count accept-established-tcp-fetch
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-tcp-fetch then accept
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-udp-ephemeral from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-udp-ephemeral from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-udp-ephemeral from protocol udp
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-udp-ephemeral from destination-port 49152-65535
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-udp-ephemeral then policer management-5m
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-udp-ephemeral then count accept-established-udp-ephemeral
set firewall family inet filter ACCEPT_ESTABLIDHED term accept-established-udp-ephemeral then accept
set firewall family inet filter ACCEPT_ALL apply-flags omit
set firewall family inet filter ACCEPT_ALL term accept-all-tcp from protocol tcp
set firewall family inet filter ACCEPT_ALL term accept-all-tcp then count accept-all-tcp
set firewall family inet filter ACCEPT_ALL term accept-all-tcp then log
set firewall family inet filter ACCEPT_ALL term accept-all-tcp then syslog
set firewall family inet filter ACCEPT_ALL term accept-all-tcp then accept
set firewall family inet filter ACCEPT_ALL term accept-all-udp from protocol udp
set firewall family inet filter ACCEPT_ALL term accept-all-udp then count "accept-all-udp;"
set firewall family inet filter ACCEPT_ALL term accept-all-udp then log
set firewall family inet filter ACCEPT_ALL term accept-all-udp then syslog
set firewall family inet filter ACCEPT_ALL term accept-all-udp then accept
set firewall family inet filter ACCEPT_ALL term accept-all-igmp from protocol igmp
set firewall family inet filter ACCEPT_ALL term accept-all-igmp then count accept-all-igmp
set firewall family inet filter ACCEPT_ALL term accept-all-igmp then log
set firewall family inet filter ACCEPT_ALL term accept-all-igmp then syslog
set firewall family inet filter ACCEPT_ALL term accept-all-igmp then accept
set firewall family inet filter ACCEPT_ALL term ACCEPT_ICMP from protocol icmp
set firewall family inet filter ACCEPT_ALL term ACCEPT_ICMP then count accept-all-icmp
set firewall family inet filter ACCEPT_ALL term ACCEPT_ICMP then log
set firewall family inet filter ACCEPT_ALL term ACCEPT_ICMP then syslog
set firewall family inet filter ACCEPT_ALL term ACCEPT_ICMP then accept
set firewall family inet filter ACCEPT_ALL term accept-all-unknown then count accept-all-unknown
set firewall family inet filter ACCEPT_ALL term accept-all-unknown then log
set firewall family inet filter ACCEPT_ALL term accept-all-unknown then syslog
set firewall family inet filter ACCEPT_ALL term accept-all-unknown then accept
set firewall family inet filter ACCEPT_WEB apply-flags omit
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB from source-prefix-list mgmt-prefixes
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB from protocol tcp
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB from destination-port http
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB from destination-port https
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB then policer management-5m
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB then count ACCEPT_WEB
set firewall family inet filter ACCEPT_WEB term ACCEPT_WEB then accept
set firewall family inet filter ACCEPT_DNS apply-flags omit
set firewall family inet filter ACCEPT_DNS term ACCEPT_DNS from source-prefix-list dns-servers
set firewall family inet filter ACCEPT_DNS term ACCEPT_DNS from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_DNS term ACCEPT_DNS from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_DNS term ACCEPT_DNS from protocol udp
set firewall family inet filter ACCEPT_DNS term ACCEPT_DNS from source-port 53
set firewall family inet filter ACCEPT_DNS term ACCEPT_DNS then policer management-1m
set firewall family inet filter ACCEPT_DNS term ACCEPT_DNS then count ACCEPT_DNS
set firewall family inet filter ACCEPT_DNS term ACCEPT_DNS then accept
set firewall family inet filter ACCEPT_MULTICAST apply-flags omit
set firewall family inet filter ACCEPT_MULTICAST term ACCEPT_PIM filter ACCEPT_PIM
set firewall family inet filter ACCEPT_MULTICAST term ACCEPT_MSDP filter ACCEPT_MSDP
set firewall family inet filter ACCEPT_PIM apply-flags omit
set firewall family inet filter ACCEPT_PIM term ACCEPT_PIM from source-prefix-list mgmt-prefixes
set firewall family inet filter ACCEPT_PIM term ACCEPT_PIM from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_PIM term ACCEPT_PIM from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_PIM term ACCEPT_PIM from protocol pim
set firewall family inet filter ACCEPT_PIM term ACCEPT_PIM then count ACCEPT_PIM
set firewall family inet filter ACCEPT_PIM term ACCEPT_PIM then accept
set firewall family inet filter ACCEPT_MSDP term ACCEPT_MSDP apply-flags omit
set firewall family inet filter ACCEPT_MSDP term ACCEPT_MSDP from source-prefix-list mgmt-prefixes
set firewall family inet filter ACCEPT_MSDP term ACCEPT_MSDP from destination-prefix-list router-ipv4
set firewall family inet filter ACCEPT_MSDP term ACCEPT_MSDP from destination-prefix-list router-ipv4-logical-systems
set firewall family inet filter ACCEPT_MSDP term ACCEPT_MSDP from protocol tcp
set firewall family inet filter ACCEPT_MSDP term ACCEPT_MSDP from source-port 639
set firewall family inet filter ACCEPT_MSDP term ACCEPT_MSDP then count ACCEPT_MSDP
set firewall family inet filter ACCEPT_MSDP term ACCEPT_MSDP then accept
set firewall policer per-interface-arp-limiter if-exceeding bandwidth-limit 2m
set firewall policer per-interface-arp-limiter if-exceeding burst-size-limit 32k
set firewall policer per-interface-arp-limiter then discard
set firewall policer management-5m if-exceeding bandwidth-limit 5m
set firewall policer management-5m if-exceeding burst-size-limit 625k
set firewall policer management-5m then discard
set firewall policer management-1m if-exceeding bandwidth-limit 1m
set firewall policer management-1m if-exceeding burst-size-limit 625k
set firewall policer management-1m then discard
set firewall policer limit-200mbps if-exceeding bandwidth-limit 200m
set firewall policer limit-200mbps if-exceeding burst-size-limit 20m
set firewall policer limit-200mbps then discard
set firewall policer limit-300mbps if-exceeding bandwidth-limit 300m
set firewall policer limit-300mbps if-exceeding burst-size-limit 50m
set firewall policer limit-300mbps then discard
set firewall policer limit-1.2Gbps if-exceeding bandwidth-limit 1200000000
set firewall policer limit-1.2Gbps if-exceeding burst-size-limit 100m
set firewall policer limit-1.2Gbps then discard





docker run -d --platform linux/amd64 --name local_irrd --network irrd-network -v /Users/lfurtado/Documents/code/Network-Automation/local_irrd/irrd.yaml:/etc/irrd.yaml -p 8043:8043 -p 8080:8080 irrd-with-twisted /usr/local/bin/twistd -n irrd --config /etc/irrd.yaml

docker exec -it irrd_local /bin/sh

=======
1) Docker-compose up --build
docker-compose up --build


2) Test access to the API
curl -X POST http://127.0.0.1:8080/v1/submit/ \
  -H "Content-Type: application/json" \
  -d '{
        "objects": [{
          "object_text": "route:         192.0.2.0/24\norigin:        AS12345\nmnt-by:        EXAMPLE-MNT\nsource:        IRRD"
        }],
        "passwords": ["your_password"]
      }'

curl -X POST http://127.0.0.1:8080/submit/ \
  -H "Content-Type: application/json" \
  -d '{"objects": [{"object_text": "route: 192.0.2.0/24\norigin: AS12345\nmnt-by: EXAMPLE-MNT\nsource: ALTDB"}], "passwords": ["your_password"]}'

http://127.0.0.1:8080/v1/status/

3) Verify IRRD logs
cat /var/log/irrd/irrd.log

4) Upgrade database schema
docker-compose run --rm irrd export IRRD_CONFIG_FILE=/etc/irrd/irrd.yaml
docker-compose run --rm -e IRRD_CONFIG_FILE=/etc/irrd/irrd.yaml irrd python -m alembic -c /app/irrd/alembic.ini upgrade head
docker-compose exec irrd python -m alembic -c /app/irrd/alembic.ini upgrade head
docker-compose exec postgres psql -U irrd -d irrd -c "\dt"

5) Create a MD5 password to your MAINTNER object
openssl passwd -1 Juniper

6) Insert MAINTNER objects to the database
docker-compose exec postgres psql -U irrd -d irrd -c "INSERT INTO rpsl_objects (rpsl_pk, object_text, source, object_class, parsed_data) VALUES (
  'MAINT-TEST',
  E'mntner:          MAINT-TEST\n\
descr:           Maintainer for local testing\n\
admin-c:         MAINT-TEST\n\
tech-c:          MAINT-TEST\n\
upd-to:          test@example.com\n\
auth:            MD5-PW \$1\$1dwDrK3S\$4U0XfqK1qS/07BvguD6qQ0\n\
mnt-by:          MAINT-TEST\n\
source:          IRRD',
  'IRRD',
  'mntner',
  E'{}'::json
);"

docker-compose exec postgres psql -U irrd -d irrd -c "SELECT rpsl_pk, source, object_class, parsed_data FROM rpsl_objects WHERE rpsl_pk = 'MAINT-TEST';"

docker-compose exec postgres psql -U irrd -d irrd -c "INSERT INTO rpsl_objects (rpsl_pk, object_text, source, object_class, parsed_data) VALUES (
  'MAINT-AS268151',
  E'mntner:          MAINT-AS268151\n\
descr:           3R INTERNET\n\
admin-c:         RUDSONCOSTA\n\
tech-c:          RUDSONCOSTA\n\
upd-to:          noc@3rinternet.com.br\n\
auth:            MD5-PW \$1\$1dwDrK3S\$4U0XfqK1qS/07BvguD6qQ0\n\
mnt-by:          MAINT-AS268151\n\
source:          IRRD',
  'IRRD',
  'mntner',
  E'{}'::json
);"

docker-compose exec postgres psql -U irrd -d irrd -c "SELECT rpsl_pk, source, object_class, parsed_data FROM rpsl_objects WHERE rpsl_pk = 'MAINT-AS268151';"

docker-compose exec postgres psql -U irrd -d irrd -c "UPDATE rpsl_objects SET 
  object_text = E'mntner:          MAINT-AS263324\n\
descr:           Net&Com Serviços de Informática e Telecomunicações\n\
admin-c:         RODRIGOOGOMES\n\
tech-c:          RUDSONCOSTA\n\
upd-to:          noc@netecom.com.br\n\
auth:            MD5-PW \$1\$1dwDrK3S\$4U0XfqK1qS/07BvguD6qQ0\n\
mnt-by:          MAINT-AS263324\n\
source:          IRRD',
  parsed_data = E'{}'::json
WHERE rpsl_pk = 'MAINT-AS263324';"

docker-compose exec postgres psql -U irrd -d irrd -c "SELECT rpsl_pk, source, object_class, parsed_data FROM rpsl_objects WHERE rpsl_pk = 'MAINT-AS268151';"

7) Locating and deleting records as needed:
docker-compose exec postgres psql -U irrd -d irrd -c "SELECT rpsl_pk, object_text FROM rpsl_objects WHERE object_text ILIKE '%CONTACT-TEST%';"


password: T44FwgvoxFcDn5UEykgcqw



docker-compose exec postgres psql -U irrd -d irrd -c "INSERT INTO rpsl_objects (rpsl_pk, object_text, source, object_class, parsed_data) VALUES (
  'MAINT-AS53123',
  E'mntner:          MAINT-AS53123\n\
descr:           POWER TELECOMUNICACOES\n\
admin-c:         PTLME5-NICBR\n\
tech-c:          PTLME5-NICBR\n\
upd-to:          noc@powertelecom.net.br\n\
auth:            MD5-PW \$1\$1dwDrK3S\$4U0XfqK1qS/07BvguD6qQ0\n\
mnt-by:          MAINT-AS53123\n\
source:          IRRD',
  'IRRD',
  'mntner',
  E'{}'::json
);"
