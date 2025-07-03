import json
import requests
import os
import time

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")  # Now from environment variable

# Polling settings
MEDIA_STATUS_POLL_INTERVAL = 2  # seconds
MEDIA_STATUS_POLL_TIMEOUT = 60  # seconds


def lambda_handler(event, context):
    print("EVENT:", event)
    
    method = event.get("requestContext", {}).get("http", {}).get("method")
    
    # Handle Facebook/Instagram webhook verification (GET)
    if method == "GET":
        params = event.get("queryStringParameters", {})
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return {
                "statusCode": 200,
                "body": challenge
            }
        else:
            return {
                "statusCode": 403,
                "body": "Forbidden"
            }
    
    # Handle Shopify product creation webhook (POST)
    if method == "POST":
        body = event.get("body")
        if body:
            try:
                product = json.loads(body)
            except Exception as e:
                print("Error parsing body:", e)
                return {"statusCode": 400, "body": "Invalid JSON in request body"}
            # Extract product info
            title = product.get('title', 'New Product')
            images = product.get('images', [])
            first_image_url = images[0]['src'] if images else ''
            # Custom Instagram caption
            caption = f"🚨 {title} from the Mob just dropped.\nOnly the real gone cop.\nHit the site — link in bio. 🥀\n#RoseMob #MobOnly #StreetLuxury"
            print(f"Prepared Instagram caption: {caption}")
            print(f"Image URL: {first_image_url}")
            # Post to Instagram
            access_token = os.environ.get('IG_ACCESS_TOKEN')
            ig_account_id = os.environ.get('IG_ACCOUNT_ID')
            if not access_token or not ig_account_id or not first_image_url:
                print("Missing access token, IG account ID, or image URL")
                return {"statusCode": 400, "body": json.dumps({"error": "Missing access token, IG account ID, or image URL"})}
            # Step 1: Create media container
            create_media_url = f"https://graph.facebook.com/v18.0/{ig_account_id}/media"
            media_payload = {
                "image_url": first_image_url,
                "caption": caption,
                "access_token": access_token
            }
            try:
                media_response = requests.post(create_media_url, data=media_payload, timeout=10)
                media_result = media_response.json()
            except Exception as e:
                print("Error creating media container:", e)
                return {"statusCode": 500, "body": json.dumps({"error": "Exception during media creation", "details": str(e)})}
            print(f"Media creation response: {media_result}")
            if 'id' not in media_result:
                return {"statusCode": 500, "body": json.dumps({"error": "Failed to create media container", "response": media_result})}
            container_id = media_result['id']
            # Step 1.5: Poll for media container status
            status_url = f"https://graph.facebook.com/v18.0/{container_id}?fields=status_code&access_token={access_token}"
            start_time = time.time()
            while True:
                try:
                    status_response = requests.get(status_url, timeout=10)
                    status_result = status_response.json()
                except Exception as e:
                    print("Error polling media status:", e)
                    return {"statusCode": 500, "body": json.dumps({"error": "Exception during media status polling", "details": str(e)})}
                print(f"Media status response: {status_result}")
                if status_result.get("status_code") == "FINISHED":
                    break
                if time.time() - start_time > MEDIA_STATUS_POLL_TIMEOUT:
                    print("Timeout waiting for media to be ready.")
                    return {"statusCode": 504, "body": json.dumps({"error": "Timeout waiting for media to be ready."})}
                time.sleep(MEDIA_STATUS_POLL_INTERVAL)
            # Step 2: Publish the media
            publish_url = f"https://graph.facebook.com/v18.0/{ig_account_id}/media_publish"
            publish_payload = {
                "creation_id": container_id,
                "access_token": access_token
            }
            try:
                publish_response = requests.post(publish_url, data=publish_payload, timeout=10)
                publish_result = publish_response.json()
            except Exception as e:
                print("Error publishing media:", e)
                return {"statusCode": 500, "body": json.dumps({"error": "Exception during media publish", "details": str(e)})}
            print(f"Media publish response: {publish_result}")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Post published to Instagram",
                    "result": publish_result
                })
            }
        else:
            print("No body in request")
            return {"statusCode": 400, "body": "No body in request"}
    # Default response for other methods
    return {"statusCode": 200, "body": "OK"}
