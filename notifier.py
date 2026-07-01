import requests
from winotify import Notification

def send_windows_notification(title,message):
    try:
        toast = Notification(
            app_id = "ThermalWatch",
            title=title,
            msg=message,
            duration="short"
        )
        toast.show()
        return True
    except Exception as e:
        print(f"Windows notification has failed: {e}")
        return False

def send_mobile_notification(topic,title,message):
    if not topic:
        return False
    url = f"https://ntfy.sh/{topic}"
    try:
        response = requests.post(
            url,
            data=message.encode("utf-8"),
            headers={
                "Title": title.encode("utf-8"),
                "Priority": "high"  
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Phone Notification has failed: {e}")
        return False
if __name__ == "__main__":
    print("Test Notifications Are Sending...")
    send_windows_notification(
        "ThermalWatch Test",
        "Thermal Limits Are Checking."
    )
    send_mobile_notification(
        "thermalwatch-test-umut",
        "ThermalWatch Test",
        "This Is A Test Notification."
    )