# Catalog
### Structure
{
    "projectName":,
    "catalog":{
        "ip":,
        "port":,
        "methods":[]
    }
    "broker": {
        "ip":,
        "port":,
        "clientID":
    },
    "telegramBot":{
        "token":,
        "link":
    },
    "greenhouses":[
        {
            "ghID":,
            "devID":,
            "numPlants":,
            "plantsList": [],
            "lastUpdate":
        },
    ],
    "users":[
        {
            "usrID":,
            "name":,
            "ghID":[]
        }
    ],
    "devices":[
        {
            "devID": ,
            "ghID":,
            "name": ,
            "endpoints": [],
            "endpoints_details": [
                {
                    "endpoint": "REST",
                    "address":
                },
                {
                    "endpoint": "MQTT",
                    "bn":
                    "topic": []
                }
            ],
            "resources": {
                "sensors": [
                    {
                        "sensID": ,
                        "devID": ,
                        "measurementType":,
                        "available_services": [
                            "REST",
                            "MQTT"
                        ],
                        "services_details": [
                            {
                                "service_type": "REST",
                                "uri":
                            },
                            {
                                "service_type": "MQTT",
                                "topic": []
                            }
                        ]
                        "lastUpdate": ""
                    },
                ],
                "actuators": [
                    {
                        "actID": "a_001",
                        "devID": "d_001",
                        "available_services": [
                            "REST",
                            "MQTT"
                        ],
                        "services_details": [
                            {
                                "service_type": "REST",
                                "uri":
                            },
                            {
                                "service_type": "MQTT",
                                "topic": []
                            }
                        ]
                        "lastUpdate": ""
                    },
                ]
            },
            "lastUpdate": ""
        }
    ]
}
