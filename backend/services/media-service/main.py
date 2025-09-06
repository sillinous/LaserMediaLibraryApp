import io
import os
import serial
import serial.tools.list_ports
import openai
import base64
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Response, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from PIL import Image, ImageOps

load_dotenv()

app = FastAPI(
    title="Laser Engraving Media Service",
    description="A service to process images for laser engraving and G-code generation.",
    version="1.0.0",
)

PRESETS = {
    "Default": {"laser_power": 1000, "travel_speed": 3000, "engraving_speed": 300},
    "Soft Wood": {"laser_power": 800, "travel_speed": 3000, "engraving_speed": 500},
    "Hard Wood": {"laser_power": 1000, "travel_speed": 3000, "engraving_speed": 300},
    "Leather": {"laser_power": 700, "travel_speed": 4000, "engraving_speed": 600},
    "Cardboard": {"laser_power": 500, "travel_speed": 5000, "engraving_speed": 800},
}

def process_image(image_bytes: bytes) -> Image:
    """
    Processes an image for engraving by converting it to grayscale and inverting it.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("L")  # Convert to grayscale
    image = ImageOps.invert(image)  # Invert colors
    return image

def generate_gcode_from_image(image: Image, threshold: int = 128, laser_power: int = 1000, travel_speed: int = 3000, engraving_speed: int = 300) -> str:
    """
    Generates G-code from a PIL image using a simple threshold and dot matrix method.
    """
    gcode_lines = [
        "G90",  # Absolute positioning
        "G21",  # Units to millimeters
        "M4",   # Dynamic laser power mode
        f"F{travel_speed}", # Set travel speed
    ]

    width, height = image.size
    pixels = image.load()

    for y in range(height):
        for x in range(width):
            if pixels[x, y] > threshold:
                # Move to pixel position
                gcode_lines.append(f"G0 X{x * 0.1:.2f} Y{y * 0.1:.2f}")
                # Turn laser on
                gcode_lines.append(f"G1 S{laser_power} F{engraving_speed}")
                # Move a tiny bit to make a dot
                gcode_lines.append(f"G1 X{(x + 0.05) * 0.1:.2f}")
                # Turn laser off
                gcode_lines.append("G1 S0")

    gcode_lines.extend([
        "M5",   # Turn off laser
        "G0 X0 Y0", # Return to home
    ])

    return "\n".join(gcode_lines)


@app.get("/", summary="Root endpoint")
def read_root():
    """A simple endpoint to confirm the service is running."""
    return {"message": "Welcome to the Media Service"}

@app.post("/process-image/", summary="Process an image for engraving preview")
async def create_upload_file(file: UploadFile = File(...)):
    """
    Upload an image, process it for laser engraving, and return the result for preview.
    The background is made transparent to help visualize the engraving.
    """
    contents = await file.read()
    image = process_image(contents)

    # Make the background transparent for previewing
    image = image.convert("RGBA")
    datas = image.getdata()
    newData = []
    for item in datas:
        if item[0] < 128: # Inverted image, so dark areas are the background
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    image.putdata(newData)

    # Save the processed image to an in-memory buffer
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")

@app.post("/generate-ai-image/", summary="Generate an image from a text prompt")
async def generate_ai_image(prompt: str = Query(...)):
    """
    Generates an image using the OpenAI DALL-E 3 model from a text prompt.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable.",
        )

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="b64_json",
        )
        image_data = io.BytesIO(base64.b64decode(response.data[0].b64_json))
        return StreamingResponse(image_data, media_type="image/png")
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-presets", summary="List available material presets")
def list_presets():
    """Returns a list of available material presets."""
    return {"presets": list(PRESETS.keys())}

@app.post("/generate-gcode/", summary="Generate G-code from an image")
async def generate_gcode_endpoint(
    file: UploadFile = File(...),
    preset: str | None = Query(default="Default")
):
    """
    Upload an image, process it, and generate G-code for laser engraving.
    Optionally, a `preset` can be specified to use predefined settings.
    """
    contents = await file.read()
    image = process_image(contents)

    settings = PRESETS.get(preset, PRESETS["Default"])
    gcode = generate_gcode_from_image(image, **settings)

    return Response(content=gcode, media_type="text/plain")

class GcodePayload(BaseModel):
    port: str
    gcode: str

@app.get("/list-serial-ports", summary="List available serial ports")
def list_serial_ports():
    """Returns a list of available serial ports."""
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return {"ports": ports}

@app.post("/send-gcode", summary="Send G-code to a serial port")
def send_gcode(payload: GcodePayload):
    """
    Sends G-code to the specified serial port.
    """
    try:
        with serial.Serial(payload.port, baudrate=115200, timeout=1) as ser:
            ser.write(b'\n') # Wake up grbl
            ser.reset_input_buffer()
            for line in payload.gcode.split('\n'):
                line = line.strip()
                if line:
                    ser.write((line + '\n').encode('utf-8'))
                    response = ser.readline().decode('utf-8').strip()
                    if 'error' in response:
                        raise HTTPException(status_code=400, detail=f"Engraver error: {response}")
        return {"message": "G-code sent successfully."}
    except serial.SerialException as e:
        raise HTTPException(status_code=500, detail=str(e))
