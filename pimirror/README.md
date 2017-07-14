google assistant install:

Configure a Developer Project and Account Settings:
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
4. Copy the `client_secret_<client-id>`.json file from your development machine to your device.

Install setuptools and pip for python3
	sudo python3 -m pip install --upgrade pip setuptools

Install google assistant library
    sudo python3 -m pip install --upgrade google-assistant-library

Install authorization tool:
	sudo python3 -m pip install --upgrade google-auth-oauthlib[tool]

Run the tool:
	google-oauthlib-tool --client-secrets /home/pi/client_secret_client-id.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless


dependencies:
Install feedparser
    sudo python3 -m pip install feedparser
Install pil.imagetk
    sudo apt-get install python3-pil.imagetk

copy mirror repo