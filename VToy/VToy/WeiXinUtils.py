

class WeiXinUtils:

    @staticmethod
    def DeviceInfo(devId="001",mac="123456789ABC",connect_protocol="4|1|2|3", auth_key='',close_strategy='1',conn_strategy='1',crypt_method='0',auth_ver='1',manu_mac_pos='-1',ser_mac_pos='-2'):
        """  DeviceInfo list   
        {
            "device_num":"2",
            "device_list":[
                {
                    "id":"dev1",
                    "mac":"123456789ABC",
                    "connect_protocol":"1|2",
                    "auth_key":"",
                    "close_strategy":"1",
                    "conn_strategy":"1",
                    "crypt_method":"0",
                    "auth_ver":"1",
                    "manu_mac_pos":"-1",
                    "ser_mac_pos":"-2"
                }
            ],
            "op_type":"0"
        }
        """
        DeviceInfo = dict()
        DeviceInfo['id'] = devId
        DeviceInfo['mac'] = mac
        DeviceInfo['connect_protocol'] = connect_protocol
        DeviceInfo['auth_key'] = auth_key
        DeviceInfo['close_strategy'] = close_strategy
        DeviceInfo['conn_strategy'] = conn_strategy
        DeviceInfo['crypt_method'] = crypt_method
        DeviceInfo['auth_ver'] = auth_ver
        DeviceInfo['manu_mac_pos'] = manu_mac_pos
        DeviceInfo['ser_mac_pos'] = ser_mac_pos

        return DeviceInfo
