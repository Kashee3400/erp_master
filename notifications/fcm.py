"""Server Side FCM sample.

Firebase Cloud Messaging (FCM) can be used to send messages to clients on iOS,
Android and Web.

This sample uses FCM to send two types of messages to clients that are subscribed
to the `news` topic. One type of message is a simple notification message (display message).
The other is a notification message (display notification) with platform specific
customizations. For example, a badge is added to messages that are sent to iOS devices.
"""

import argparse
import json
import requests
import google.auth.transport.requests

from google.oauth2 import service_account

PROJECT_ID = "kashee-e-dairy"
BASE_URL = "https://fcm.googleapis.com"
FCM_ENDPOINT = "v1/projects/" + PROJECT_ID + "/messages:send"
FCM_URL = BASE_URL + "/" + FCM_ENDPOINT
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]


# [START retrieve_access_token]
def _get_access_token():
    """Retrieve a valid access token that can be used to authorize requests.

    :return: Access token.
    """
    credentials = service_account.Credentials.from_service_account_file(
        "K:\service-account-file.json", scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


# [END retrieve_access_token]


def _send_fcm_message(fcm_message):
    """Send HTTP request to FCM with given message.

    Args:
    fcm_message: JSON object that will make up the body of the request.
    """
    # [START use_access_token]
    headers = {
        "Authorization": "Bearer " + _get_access_token(),
        "Content-Type": "application/json; UTF-8",
    }
    # [END use_access_token]
    resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

    if resp.status_code == 200:
        return True,resp.text
    else:
        return False, resp.text


def _build_common_message():
    """Construct common notifiation message.
    Construct a JSON object that will be used to define the
    common parts of a notification message that will be sent
    to any app instance subscribed to the news topic.
    """
    return {
        "message": {
            "topic": "news",
            "notification": {
                "title": "FCM Notification",
                "body": "Notification from FCM",
            },
        }
    }


def _send_device_specific_notification(device_token, notification):
    message = {"message": {"token": device_token, "notification": notification}}
    sent,info = _send_fcm_message(fcm_message=message)
    if sent:
        print(F"Message {info} sent to user's device")
    else:
        print(f"Message Not Sent")
        print(info)


def _build_override_message():
    """Construct common notification message with overrides.

    Constructs a JSON object that will be used to customize
    the messages that are sent to iOS and Android devices.
    """
    fcm_message = _build_common_message()

    apns_override = {
        "payload": {"aps": {"badge": 1}},
        "headers": {"apns-priority": "10"},
    }

    android_override = {"notification": {"click_action": "android.intent.action.MAIN"}}

    fcm_message["message"]["android"] = android_override
    fcm_message["message"]["apns"] = apns_override

    return fcm_message


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--message")
    args = parser.parse_args()
    if args.message and args.message == "common-message":
        common_message = _build_common_message()
        print("FCM request body for message using common notification object:")
        print(json.dumps(common_message, indent=2))
        _send_fcm_message(common_message)
    elif args.message and args.message == "override-message":
        override_message = _build_override_message()
        print("FCM request body for override message:")
        print(json.dumps(override_message, indent=2))
        _send_fcm_message(override_message)
    elif args.message and args.message == "device-message":
        token = "fJQLRDRaTt2DcZhgn5nzrW:APA91bFb0htbcPcdbDn3WGYGnyech9exBeQYYKHzmPGefpS7WcIWBJ2QQfj672UGu-_slHvnmCO8sEIRsfADgn5m34S3CCgEt2bHb6OsBBn4cSOi2-KvLiw"
        notification = {
            "title":"Test Notification",
            "body":"Test message",
        }
        _send_device_specific_notification(device_token=token,notification=notification)
    else:
        print(
            """Invalid command. Please use one of the following commands:
                python fcm.py --message=common-message
                python fcm.py --message=override-message
                python fcm.py --message=device-message"""
        )


if __name__ == "__main__":
    main()
