GCP_TEST_MACHINE_LIST = {
    "europe-west3-a": [
        "sshkeys-11",
        "sshkeys-12",
        "hadoop-2",
        "hadoop-3",
        "mssql-16",
        "mimikatz-14",
        "mimikatz-15",
        "tunneling-9",
        "tunneling-10",
        "tunneling-11",
        "tunneling-12",
        "tunneling-13",
        "zerologon-25",
    ],
    "europe-west1-b": [
        "powershell-3-45",
        "powershell-3-46",
        "powershell-3-47",
        "powershell-3-48",
        "log4j-logstash-55",
        "log4j-logstash-56",
        "log4j-solr-49",
        "log4j-solr-50",
        "log4j-tomcat-51",
        "log4j-tomcat-52",
    ],
}

DEPTH_2_A = {
    "europe-west3-a": [
        "sshkeys-11",
        "sshkeys-12",
    ]
}


DEPTH_1_A = {
    "europe-west3-a": ["hadoop-2", "hadoop-3", "mssql-16", "mimikatz-14", "mimikatz-15"],
    "europe-west1-b": [
        "log4j-logstash-55",
        "log4j-logstash-56",
        "log4j-solr-49",
        "log4j-solr-50",
        "log4j-tomcat-51",
        "log4j-tomcat-52",
    ],
}

DEPTH_3_A = {
    "europe-west3-a": [
        "tunneling-9",
        "tunneling-10",
        "tunneling-11",
        "mimikatz-15",
    ],
    "europe-west1-b": [
        "powershell-3-45",
        "powershell-3-46",
        "powershell-3-47",
        "powershell-3-48",
    ],
}

DEPTH_4_A = {
    "europe-west1-b": [
        "tunneling-9",
        "tunneling-10",
        "tunneling-12",
        "tunneling-13",
    ],
}


POWERSHELL_EXPLOITER_REUSE = {
    "europe-west1-b": [
        "powershell-3-46",
    ]
}

ZEROLOGON = {
    "europe-west3-a": [
        "zerologon-25",
    ],
}

WMI_AND_MIMIKATZ = {
    "europe-west3-a": [
        "mimikatz-14",
        "mimikatz-15",
    ]
}

SMB_PTH = {"europe-west3-a": ["mimikatz-15"]}

GCP_SINGLE_TEST_LIST = {
    "test_depth_2_a": DEPTH_2_A,
    "test_depth_1_a": DEPTH_1_A,
    "test_depth_3_a": DEPTH_3_A,
    "test_depth_4_a": DEPTH_4_A,
    "test_powershell_exploiter_credentials_reuse": POWERSHELL_EXPLOITER_REUSE,
    "test_zerologon_exploiter": ZEROLOGON,
    "test_wmi_and_mimikatz_exploiters": WMI_AND_MIMIKATZ,
    "test_smb_pth": SMB_PTH,
}
