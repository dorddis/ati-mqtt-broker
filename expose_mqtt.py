import ngrok
import asyncio

async def create_tunnel():
    # Set your ngrok auth token
    ngrok.set_auth_token("30ilj8Rj8hAmLUtOU8OmOqsotYs_4XPhwPJ64iaN4Z1pAbLS6")
    
    # Create an HTTP tunnel to port 9001 (WebSockets)
    listener = await ngrok.connect(9001, "http")
    print(f"MQTT WebSocket broker exposed at: {listener.url()}")
    print(f"Use this URL in your MQTT client with WebSocket protocol")
    
    # Keep the tunnel open
    try:
        input("Press Enter to close the tunnel...")
    except KeyboardInterrupt:
        pass
    finally:
        await listener.close()

if __name__ == "__main__":
    asyncio.run(create_tunnel())