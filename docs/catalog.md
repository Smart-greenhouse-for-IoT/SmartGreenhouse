# Catalog

### Metodi
"GET":[
                "device",   #return all devices
                "device?devID=",    #return device with devID specified
                "device?name=", #return device with specified name
                "device/recentID",  #return the ID of the latest added device
                "device/sensors?devID=",    #return sensors associated to device devID
                "device/actuators?devID="   #return actuators associated to device devID
                "broker",   #return broker info
                "catalogInfo",  #return catalog info
                "projectInfo",  #return project info
                "telegramInfo", #return telegram info
                "greenhouse",   #return all greenhouses
                "greenhouse?ghID=", #return greenhouse with specified ghID
                "greenhouse?usrID=",    #return greenhouses with specifeid usrID #TODO:deve ritornare più greenhouse se associate a user
                "greenhouse?devID=",    #return greenhouse asscoiated to device devID
                "user", #return all users
                "user?usrID=", #return user with specified usrID
                "user?usrID=&plant=",   #return the plant if present in owned plants
                "plant?devID=&sensID="  #return plant associated to sensor sensID and device devID
            ]
        },
        {
            "POST":[
                "updateDevices",
                "addDevice",
                "addUser",
                "addGreenhouse",
                "addPlant?usrID=",
                "addService",
            ]
        },
        {
            "PUT":[
                "updateDevice",
                "updateUser",
                "updateGreenhouse",
                "updateService"
            ]

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
            "gh_params":{
                "temp": "",
                "CO2": "",
                "hum": ""
            },
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
