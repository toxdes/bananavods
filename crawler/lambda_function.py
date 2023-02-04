from crawl import main
def lambda_handler(event, context):
    message = 'Hello from lambda'  
    main()
    return { 
        'message' : message
    }