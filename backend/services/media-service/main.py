import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image, ImageOps

app = FastAPI(
    title="Laser Engraving Media Service",
    description="A service to process images for laser engraving.",
    version="1.0.0",
)

def process_image_for_engraving(image_bytes: bytes) -> io.BytesIO:
    """
    Processes an image for laser engraving by converting it to grayscale,
    inverting it, and making the white background transparent.
    """
    # Open the image from the in-memory bytes
    image = Image.open(io.BytesIO(image_bytes))

    # 1. Convert to grayscale ('L' mode)
    # This simplifies the image to shades of gray, which is what most
    # laser engravers work with.
    image = image.convert("L")

    # 2. Invert the image
    # In laser engraving, black areas are typically engraved. Inverting the image
    # means that the dark parts of the original image will be engraved.
    image = ImageOps.invert(image)

    # 3. Make the background transparent
    # We will convert the image to RGBA to have an alpha channel.
    # We then find all pixels that were originally white (now black after inversion)
    # and make them fully transparent. This prevents the background from being engraved.
    image = image.convert("RGBA")
    datas = image.getdata()

    newData = []
    for item in datas:
        # If the pixel was black (0) after inversion, make it transparent
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            newData.append((255, 255, 255, 0))  # Add a transparent pixel
        else:
            newData.append(item)  # Keep the original pixel

    image.putdata(newData)

    # Save the processed image to an in-memory buffer
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)

    return buffer

@app.get("/", summary="Root endpoint")
def read_root():
    """A simple endpoint to confirm the service is running."""
    return {"message": "Welcome to the Media Service"}

@app.post("/process-image/", summary="Process an image for engraving")
async def create_upload_file(file: UploadFile = File(...)):
    """
    Upload an image, process it for laser engraving, and return the result.

    The processing pipeline is as follows:
    1.  **Convert to Grayscale:** Removes color information.
    2.  **Invert Colors:** Dark areas become light, light areas become dark.
    3.  **Make White Background Transparent:** Ensures the background is not engraved.

    The processed image is returned as a PNG file.
    """
    # Read the contents of the uploaded file
    contents = await file.read()

    # Process the image
    processed_image_buffer = process_image_for_engraving(contents)

    # Return the processed image as a streaming response
    return StreamingResponse(processed_image_buffer, media_type="image/png")
