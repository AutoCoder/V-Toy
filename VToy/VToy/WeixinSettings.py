# -*- coding: utf-8 -*-
"""
Weixin mp settings for VToy project.

This file will include :

APP_ID

APP_SECRET 

ACCESSTOKEN_EXPIRE (unit : second)

"""

wx_mp_token = 'vtoy'

APP_ID = "wxe10a58cb12e36d7d"

APP_SECRET = "8643cc7ba2214bfd2b1447601e0078e2"

MP_ID = "gh_2fb6f6563f31"

ACCESSTOKEN_EXPIRE = 7200 # second

DEVICE_HEARTBEAT_FREQ = 2*60 # 2 minutes

CS_MSG_AVAILABLE_DURATION = 48 * 3600 


#if we want chinese menu name, we need convert unicode to utf8, before sending it to wx
CUSTOM_MENU = {
	"button":[
	{
		"type":"click",
		"name": "ConnectWIFI",
		"key":"VTOY_CONNECT_WIFI"
	},
	{
		"type":"view",
		"name": "webpage",
		"url":"http://121.40.99.4/vtoy/airkiss/"
	},
	{
		"name":"menu",
		"sub_button":[
		{
			"type":"view", 
			"name":"baidu", 
			"url":"http://www.baidu.com/"
		},
		{
			"type":"view", 
			"name":"sohu", 
			"url":"http://www.sohu.com/"
		}]
	}]
}
