# Tutorials
## Setup hardware:
1. 安装好你的树莓派在PiMirror背后。插入Mini Microphone to Raspberry Pi 的USB接口。
2. 烧写SD卡，到[raspberrypi.org](www.raspberrypi.org)下载最新的镜像，并使用[Win32 Disk Imager](https://sourceforge.net/projects/win32diskimager/),把镜像烧录到SD卡。
2. 烧录完成后，把SD卡插入树莓派，用配备的USB线，连接屏幕驱动板的USB到树莓派的电源，连接屏幕的电源，接上USB 鼠标和键盘，并打开开关。
3. 打开开关后树莓派应该能够正常启动。启动完成后，先让显示器横放，访问后就可以开始软件配置了

## 软件配置：
### 配置Google Assistant
1. In the Cloud Platform Console, go to the Projects page. Select an existing project or create a new project.
    [GO TO THE PROJECTS PAGE](https://console.cloud.google.com/project)
2. Enable the Google Assistant API on the project you selected (see the Terms of Service).
    [ENABLE THE API](https://console.developers.google.com/apis/api/embeddedassistant.googleapis.com/overview)
    Click Enable.
3. Create an OAuth Client ID with the following steps:
    a. Create the client ID. 
    [CREATE AN OAUTH CLIENT ID](https://console.developers.google.com/apis/credentials/oauthclient)
    b. You may need to set a product name for the product consent screen. On the **OAuth consent screen** tab, give the product a name and click **Save**.
    c. Click **Other** and give the client ID a name.
    d. Click **Create**. A dialog box appears that shows you a client ID and secret. (No need to remember or save this, just close the dialog.)
    e. Click ⬇ (at the far right of screen) for the client ID to download the client secret JSON file (client_secret_<client-id>.json).
4. Copy the `client_secret_<client-id>.json` file to `/home/pi` as `client_secret.json`

### 获取天气API from Dark Sky
1. Go to [Dark Sky API](https://darksky.net/dev/)
2. **LOG IN** or **SIGN UP** 如果你是新用户sign up 你需要根据提示验证你的邮箱。验证完毕后，再Log in
3. Log in后你可以直接就看到 **Your Secret Key**。你可以先复制下来备用，或者等下需要的时候在登陆查看。

### 安装SunFounder_PiMirror
1. Clone the repo:

    cd ~
    git clone --depth 1 https://github.com/sunfounder/SunFounder_PiMirror.git
2. install:

    cd SunFounder_PiMirror
    sudo ./install
3. 安装的时候会提示你是否已经配置好google assistant，如果已经配置好了，就选Y，如果还没有可以先选N退出，然后按照上面的教程配置Google Assistant
4. 随后会提示你输入Dark sky的Weather Secret Key，你就把上面获取的Secret Key 复制下来，然后粘贴上去并回车确认。
5. 安装完毕后会提示问你是否需要重启，如果没有别的什么事情要做就直接输入Y确认重启。 