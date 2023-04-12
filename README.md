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
    "QT_X11_NO_MITSHM=1",
    "LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1"
  ],
  "Volumes":{
    "/tmp/.X11-unix":{}
  },
  "WorkingDir": "/app",
  "Cmd": ["python3", "demo.py"],
  "HostConfig": {
    "AutoRemove":true,
    "Binds":[
      "/tmp/.X11-unix/:/tmp/.X11-unix"
    ],
    "Devices":[
        {
            "PathOnHost": "/dev/video0",
            "PathInContainer": "/dev/video0",
            "CgroupPermissions": "rwm"
        }
    ],
    "Runtime":"nvidia",
    "NetworkMode":"host"
  }
}
```

# 1. 模型訓練

<p align="center">
  <img width="600" src="pic\f1.png">
</p>

> 操作環境 : 本機的Azure Custom Vision portal

* 模型應用 : 物件分類
* 訓練資料上傳
* 模型訓練
* 模型下載

# 2. Docker安裝與映像檔建立

<p align="center">
  <img width="600" src="pic\f2.png">
</p>

> 操作環境 : Azure VM

## Docker安裝(optional)

> 若系統已安裝Docker則可以跳過，直接到`建立客製化的Docker映象檔`的部分

這部分提供兩種安裝方式，`一鍵安裝`與`逐步安裝`

### 1. 一鍵安裝

```
$ curl -fsSL https://get.docker.com | bash -s docker
```

* 執行下列指令，可以免去每次都要輸入`sudo`

```
$ sudo groupadd docker # 建立docker用戶組
$ sudo gpasswd -a $USER docker # 將當前用戶加入docker組
$ newgrp docker
```

### 2. 逐步安裝

1. 確保系統已更新至最新版本

   ```
   $ sudo apt-get update
   $ sudo apt-get upgrade
   ```

2. 透過以下命令先將 Docker 移除 ( 若是已經安裝過 Docker 的 )

   ```
   $ sudo apt-get remove docker docker-engine docker.io containerd runc
   ```

3. 安裝相依套件

   ```
   $ sudo apt-get update
   $ sudo apt-get install -y ca-certificates curl gnupg lsb-release
   ```

4. 添加Docker的官方GPG密鑰與APT的下載庫位置

   ```
   $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   
   $ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

5. 再次更新APT庫並安裝Docker

   ```
   $ sudo apt-get update
   $ sudo apt-get install -y docker-ce docker-ce-cli containerd.io
   ```

6. 確認Docker以正確安裝並啟動

   ```
   $ sudo docker run hello-world
   ```

## 建立客製化的Docker映象檔

這裡有兩種方式可以建立映像檔，1) 編寫Dockerfile和2) 從docker hub下載base image

### 1. 編寫Dockerfile

* 在 Dockerfile 所在目錄下執行

  ```
  $ docker build -t tf2.3-gpu-arm64:v0.0 .
  ```

### 2. 從base image建立客製化映像檔

* 下載適當的映象檔

  * arm 64 映像檔連結[在此](https://github.com/dusty-nv/jetson-containers)

  ```
  $ sudo docker pull nvcr.io/nvidia/l4t-tensorflow:r32.5.0-tf2.3-py3
  ```

  > 要確認本機端安裝的cuda版本與base image的tensorflow版本是否一致，才能順利啟用gpu

* 設定xhost

  ```
  $ xhost +[HostName]
  ```

  > 只須設定一次

* 啟動容器

  ```
  $ sudo docker run -it --rm -v <diretory path on pc>:<diretory path on container> --workdir <diretory path on container> -e DISPLAY=:0 -e QT_X11_NO_MITSHM=1 --device="/dev/video0:/dev/video0" -v /tmp/.X11-unix/:/tmp/.X11-unix/ --runtime=nvidia l4t-tensorflow:r32.5.0-tf2.3-py3 /bin/bash
  ```

* 啟動容器後，在該容器內安裝必要的函式庫

  ```
  $ sh setup_opencv.sh
  ```

* 執行辨識程式，確認容器功能正常

  ```
  $ python3 savedmodel_classification.py
  ```

  > 若跑出辨識視窗則表示容器功能正常，可以進行打包
  >
  > 開一個新的命令視窗，並請勿關閉容器

* 在新的終端介面執行下列語法，將其打包成Docker映象檔

  ```
  $ sudo docker commit <CONTAINER ID> tf2.3-gpu-arm64:v0.0
  ```

* 儲存成壓縮檔，以利使用

  ```
  $ sudo docker save -o <tar file name> <IMAGE ID>
  ```

* 載入Docker映像壓縮檔，確認該壓縮檔內的映像檔是否正常

  ```
  $ sudo docker load -i <tar file name>
  ```

# 3. Docker映像檔上傳與管理@ACR (Azure Container Registry)

<p align="center">
  <img width="600" src="pic\f3.png">
</p>

ACR可以用來儲存您的映像檔，詳見[官方網站](https://azure.microsoft.com/zh-tw/products/container-registry)

* 建立ACR，細節可以參考[ADVANTECH-Corp/DeviceOn-x86_Edge_AI_Solution](https://github.com/ADVANTECH-Corp/DeviceOn-x86_Edge_AI_Solution/blob/main/AutomateAILifecycle.md)，完成後可以取得密鑰

* 透過Docker登入ACR，並輸入帳密
  ```
  $ sudo docker login <URL>
  ```
  
<p align="center">
  <img width="600" src="pic\螢幕擷取畫面 2023-03-28 091102.png">
</p>

* image名稱必須加上前綴 -> `deviceonadf.azurecr.io`
  ```
  $ sudo docker tag tf2.3-gpu-arm64:v0.0 deviceonadf.azurecr.io/tf2.3-gpu-arm64:v0.0
  ```
