import asyncio
import websockets
import json
import random
import base64
import os


async def generate_fake_data():
    """Generate fake form data and encoded image for testing."""
    form_data = {
        "cameraType": random.choice(
            ["Topcon NW400", "Canon CX-1", "Optos Daytona Plus", "Other"]
        ),
        "age": random.randint(0, 100),
        "gender": random.choice(["Female", "Male", "Non-binary"]),
        "diabetesHistory": random.choice(["Yes", "No", "Unknown"]),
        "familyDiabetesHistory": random.choice(["Yes", "No", "Unknown"]),
        "weight": round(random.uniform(30, 150), 1),
        "height": round(random.uniform(100, 200), 1),
    }
    form_data["customCameraType"] = (
        f"CustomCamera{random.randint(1, 3)}"
        if form_data["cameraType"] == "Other"
        else ""
    )

    # Simulate a base64-encoded image (random binary data here for simplicity)
    fake_image_data = base64.b64encode(os.urandom(1024)).decode("utf-8")
    captured_photo = f"data:image/jpeg;base64,{fake_image_data}"

    return {
        "formData": form_data,
        "capturedPhoto": captured_photo,
    }


async def call_api(url, fake_data, semaphore):
    """Send a single request to the WebSocket API with concurrency control."""
    async with semaphore:  # Limit concurrency
        try:
            async with websockets.connect(url) as websocket:
                # Send the fake data as a JSON string
                await websocket.send(json.dumps(fake_data))
                print(f"Sent data: {json.dumps(fake_data, indent=2)}")

                # Listen for messages from the server
                while True:
                    response = await websocket.recv()
                    print(f"Received response: {response}")
                    if response.find("Invalid") != -1:
                        print("Invalid data detected, exiting...")
                        break
                    if response.find("Report generated") != -1:
                        print("Report generated, exiting...")
                        break
        except Exception as e:
            print(f"Error in WebSocket connection: {e}")


async def main():
    """Run multiple WebSocket connections in parallel with a concurrency limit."""
    url = "ws://localhost:8000/ws/process/"
    num_connections = 2000  # Number of total connections
    max_concurrent_connections = 4  # Maximum number of concurrent connections
    semaphore = asyncio.Semaphore(max_concurrent_connections)

    # Generate fake data and create tasks
    tasks = [
        call_api(url, await generate_fake_data(), semaphore)
        for _ in range(num_connections)
    ]

    # Run tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
