import json

def lambda_handler(event, context):
    body = event.get('body')
    if not body:
        return {'statusCode': 400, 'body': json.dumps('No body in event')}
    
    product = json.loads(body)
    
    title = product.get('title', 'New Product')
    description = product.get('body_html', '')
    product_url = product.get('handle', '')
    images = product.get('images', [])
    first_image_url = images[0]['src'] if images else ''
    
    # Format your social post message
    message = f"Check out our new product: {title}!\n{description[:100]}...\nBuy now: https://yourstore.myshopify.com/products/{product_url}"
    
    # TODO: Add your code to post 'message' to Instagram, Twitter, TikTok APIs here
    
    print("Prepared message for social posting:", message)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Product processed and social post prepared.')
    }
