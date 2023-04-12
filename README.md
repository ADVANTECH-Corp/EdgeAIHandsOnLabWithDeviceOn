# EdgeAIHandsOnLabWithDeviceOn
# 流程圖
<p align="center">
  <img width="600" src="pic\flow.png">
</p>
# 0. 容器建立與佈署
* 透過DeviceOn介面將ACR中的映像檔佈署到edge端設備，並建立與啟動容器
<p align="center">
  <img width="600" src="pic\Screenshot from 2022-11-29 13-50-02.png">
</p>
<p align="center">
  <img width="600" src="pic\Screenshot from 2022-11-25 09-27-47.png">
</p>
<p align="center">
  <img width="600" src="pic\Screenshot from 2022-11-30 14-47-31.png">
</p>
* 推論程式自啟動設定
```
{
  "Env": [
    "DISPLAY=:0",
    "QT_X11_NO_MITSHM=1"
  ],
  "Volumes":{
    "/tmp/.X11-unix":{},
    "/home/a":{}
  },
  "WorkingDir": "/ws",
  "Cmd": ["date"],
  "HostConfig": {
    "Binds":[
      "/tmp/.X11-unix/:/tmp/.X11-unix",
      "/home/a:/ws"
    ],
    "Devices":[
        {
            "PathOnHost": "/dev/video0",
            "PathInContainer": "/dev/video0",
            "CgroupPermissions": "rwm"
        }
    ]
  }
}
```
