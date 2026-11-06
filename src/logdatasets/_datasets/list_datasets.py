from logdatasets._datasets.templates import drone

from pathlib import Path


ait_files: list[dict[str, str]] = [
    {
        "Name": "VPN-OpenVPN",
        "LogType": "OpenVPN",
        "Paths": "/gather/vpn/logs/openvpn.log",
        "Multiple logs": False,
        "Labels": "/labels/vpn/logs/openvpn.log",
        "Labels_type": "AIT_v2",
    },
    {
        "Name": "VPN-Audit",
        "LogType": "Audit",
        "Paths": "/gather/vpn/logs/audit/audit.log",
        "Multiple logs": False,
        "Labels": None,
        "Labels_type": "AIT_v2",
    },
    {
        "Name": "VPN-Syslog",
        "LogType": "SysLog",
        "Paths": "/gather/vpn/logs/",
        "Pattern": "syslog",
        "Multiple logs": True,
        "Labels": None,
        "Labels_type": "AIT_v2",
    },    
    {
        "Name": "Intranet-Audit",
        "LogType": "Audit",
        "Paths": "/gather/intranet_server/logs/audit/audit.log",
        "Multiple logs": False,
        "Labels": "/labels/intranet_server/logs/audit/audit.log",  
        "Labels_type": "AIT_v2",
    },
    {
        "Name": "Intranet-Apache",
        "LogType": "Apache",
        "Paths": "/gather/intranet_server/logs/apache2",
        "Pattern": "-access.log",
        "Multiple logs": True,
        "Labels": "/labels/intranet_server/logs/apache2/", 
        "Labels_type": "AIT_v2",
    },
    {
        "Name": "Intranet-Syslog",
        "LogType": "SysLog",
        "Paths": "/gather/intranet_server/logs/",
        "Pattern": "syslog",
        "Multiple logs": True,
        "Labels": None, 
        "Labels_type": "AIT_v2",
    },
    {
        "Name": "FileShare-Audit",
        "LogType": "Audit",
        "Paths": "/gather/internal_share/logs/audit/audit.log",
        "Multiple logs": False,
        "Labels": "/labels/internal_share/logs/audit/audit.log", 
        "Labels_type": "AIT_v2",

    },
    {
        "Name": "FileShare-Syslog",
        "LogType": "SysLog",
        "Paths": "/gather/internal_share/logs/",
        "Pattern": "syslog",
        "Multiple logs": True,
        "Labels": None, 
        "Labels_type": "AIT_v2",
    },
    {
        "Name": "Firewall-Audit",
        "LogType": "Audit",
        "Paths": "/gather/inet-firewall/logs/audit/audit.log",
        "Multiple logs": False,
        "Labels": None, 
        "Labels_type": "AIT_v2",
    },
    {
        "Name": "Firewall-Syslog",
        "LogType": "SysLog",
        "Paths": "/gather/inet-firewall/logs/",
        "Pattern": "syslog",
        "Multiple logs": True,
        "Labels": None,
        "Labels_type": "AIT_v2",
    },
    {
        "Name": "Firewall-DNSmasq",
        "LogType": "DNSmasq",
        "Paths": "/gather/inet-firewall/logs/dnsmasq.log",
        "Multiple logs": False,
        "Labels": "/labels/inet-firewall/logs/dnsmasq.log",
        "Labels_type": "AIT_v2",
    },
]

def ait_config(name: str) ->  dict[str, str | list]:
    return {
        "List": ait_files,
        "URL": f"https://zenodo.org/records/5789064/files/{name}.zip?download=1"
    }


overall_datasets: dict[str, dict[str, str | list] | dict[str, str]] = {
    "AIT_v2_fox" : ait_config("fox"),
    "AIT_v2_harrison": ait_config("harrison"),
    "AIT_v2_russellmitchell": ait_config("russellmitchell"),
    "AIT_v2_shaw": ait_config("shaw"),
    "AIT_v2_santos": ait_config("santos"),
    "AIT_v2_wardbeck": ait_config("wardbeck"),
    "AIT_v2_wheeler": ait_config("wheeler"),
    "AIT_v2_wilson": ait_config("wilson"),
    "LogHub_HDFS": {
        "Name": "LogHub_HDFS",
        "LogType": "HDFS",
        "Paths": "/HDFS.log",
        "Multiple logs": False,
        "Labels": "/preprocessed/anomaly_label.csv",
        "Labels_type": "HDFS",
        "URL": "https://zenodo.org/records/8196385/files/HDFS_v1.zip?download=1"
    },
    "LogHub_BGL": {
        "Name": "LogHub_BGL",
        "LogType": "BGL",
        "Paths": "/BGL.log",
        "Multiple logs": False,
        "Labels": None,
        "URL": "https://zenodo.org/records/8196385/files/BGL.zip?download=1"
    },
    "LogHub_Thunderbird": {
        "Name": "LogHub_Thunderbird",
        "LogType": "BGL",
        "Paths": "/Thunderbird.log",
        "Multiple logs": False,
        "Labels": None,
        "URL": "https://zenodo.org/records/8196385/files/Thunderbird.tar.gz?download=1"
    },
    "AInception": {
        "URL": "https://zenodo.org/records/17659656/files/SL100.zip?download=1",
        "List": [
            {
                "Name": "Drone-Audit",
                "LogType": "Audit",
                "Paths": "/SL100/sl100-raw-data/2nd Data Extraction_with_suricata_netflows/audit.log",
                "Multiple logs": False,
                "Labels": "/SL100/sl100-labeled-data/audit.log.json", 
                "Labels_type": "SL100",
            },
            {
                "Name": "Drone-Logs",
                "LogType": "DroneSL100",
                "Paths": "/SL100/sl100-raw-data/2nd Data Extraction_with_suricata_netflows/drone_flight_logs.log",
                "Multiple logs": False,
                "Labels": "/SL100/sl100-labeled-data/drone_flight_logs.log.json", 
                "Labels_type": "SL100",
                "regex": r'(?P<Date>\S+) (?P<Time>\S+) (?P<Content>.*)',
                "templates": drone.templates
            },
        ]
    }
}

