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
            "devID": [],
            "usrID":,
            "maxNumPlants":,
            "plantsList": [
                {
                    "plant":"",
                    "th_min":,
                    "th_max":,
                    "devID":, 
                    "sensID":,
                    "actID":
                ],
                }
            ],
            #TODO: microservice associated to GH
            "lastUpdate":
        },
    ],
    "users":[
        {
            "usrID":,
            "name":,
            "ghID":[],
            "ownedPlants":[
                {
                    "name":
                    "th_min",
                    "th_max"
                }
            ]
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
                        "device_name": ,
                        "sensID": ,
                        "devID": ,
                        "pin": 1,
                        "measurementType":,
                        "units":,
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
                        "device_name": ,
                        "actID": "a_001",
                        "devID": "d_001",
                        "pin": 18,
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
    ],
    "services":[#TODO]
}
