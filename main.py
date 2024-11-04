import json
from telethon import TelegramClient, functions
import requests

# Load config
print("Loading config...")
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize Telegram client
print("Initializing Telegram client...")
client = TelegramClient('session', config["api_id"], config["api_hash"])

# Load username list
print("Loading username list...")
with open('usernames.txt', 'r') as f:
    usernames = [line.strip() for line in f if line.strip()]

# Check username availability on Fragment
def check_username_availability(username):
    print(f"Checking availability for: {username}")
    url = f"https://fragment.com/username/{username}"
    response = requests.get(url)
    
    # Placeholder condition; adjust based on actual response
    if "Available" in response.text:
        print(f"{username} is available")
        return True
    elif "Taken" in response.text or "Unavailable" in response.text:
        print(f"{username} is not available")
        return False
    else:
        print(f"Unexpected response for {username}")
        return None

# Function to create a channel and claim the username
async def create_channel_and_claim_username(username):
    # Check availability
    if check_username_availability(username):
        try:
            print(f"Username {username} is available. Creating channel...")

            # Step 1: Create the channel without username
            result = await client(functions.channels.CreateChannelRequest(
                title="Channel for " + username,
                about="Channel to claim the username"
            ))
            channel_id = result.chats[0].id
            print(f"Channel created with ID: {channel_id}")

            # Step 2: Attempt to assign the username to the created channel
            await client(functions.channels.UpdateUsernameRequest(
                channel=channel_id,
                username=username
            ))
            print(f"Successfully claimed username: {username} for the channel.")
            
            # Stop checking this username by returning from the function
            return True  # Indicate that the username was claimed
        except Exception as e:
            print(f"Failed to claim username {username}. Error: {e}")
    else:
        print(f"Username {username} is not available. Skipping channel creation.")

    return False  # Indicate that the username was not claimed

# Main loop to check each username
async def main():
    await client.start()
    print("Connected to Telegram.")
    claimed_usernames = set()  # Set to track claimed usernames

    while True:
        for username in usernames:
            # Skip checking if username is already claimed
            if username in claimed_usernames:
                print(f"Username {username} has already been claimed. Skipping...")
                continue
            
            claimed = await create_channel_and_claim_username(username)
            if claimed:
                claimed_usernames.add(username)  # Add to claimed usernames

# Run the main function
with client:
    client.loop.run_until_complete(main())
