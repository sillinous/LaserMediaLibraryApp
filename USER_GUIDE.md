# Laser Engraver Application User Guide

This guide provides instructions on how to set up and use the laser engraver application.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [How to Run the Application](#how-to-run-the-application)
- [Using the Web Interface](#using-the-web-interface)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)

## Overview

This application provides a simple web-based interface to control a laser engraver. It allows you to upload an image, convert it to G-code, and send it to your engraver for printing.

The application consists of two main parts:
- A **frontend** web interface for user interaction.
- A **backend** service that handles image processing, G-code generation, and communication with the engraver.

## Requirements

To use this application, you will need:
- **Docker** and **Docker Compose** installed on your computer.
- A **laser engraver** that is compatible with GRBL-style G-code.
- A **USB cable** to connect your computer to the laser engraver.

## How to Run the Application

1.  **Clone the repository** to your local machine.
2.  **Connect your laser engraver** to your computer via USB.
3.  **Open a terminal** and navigate to the root directory of the project.
4.  **Run the application** using Docker Compose:
    ```bash
    docker-compose up --build
    ```
5.  Once the application is running, you can access the web interface at `http://localhost:5173`.

## Using the Web Interface

The web interface provides a simple step-by-step process for engraving an image.

### 1. Select Device and Material
- **Serial Port:** The application will automatically detect available serial ports on your computer. Select the serial port corresponding to your laser engraver from the dropdown menu.
- **Material Preset:** Select a material from the dropdown menu. This will automatically configure the laser power and speed settings for optimal results with that material.

### 2. Create Your Design
You have two options for creating a design:

- **Upload an Image:** Click the "Choose File" button to select an image from your computer.
- **Generate with AI:** Enter a text description of the image you want to create (e.g., "a majestic lion head") and click the "Generate" button. This will use an AI model to create an image from your prompt.

A preview of the processed image will be displayed.

### 3. Start Engraving
- Once you have selected a serial port and an image, click the "Start Engraving" button.
- The application will generate G-code from your image and send it to the engraver.
- You can monitor the status of the process in the "Status" section.

### 4. View G-code
- The generated G-code will be displayed in a text area at the bottom of the page. This can be useful for debugging or for use with other G-code sending applications.

## API Endpoints

The backend service exposes several API endpoints that can be used for programmatic control. The service runs at `http://localhost:8000`.

- `GET /list-serial-ports`: Returns a JSON object with a list of available serial ports.
- `GET /list-presets`: Returns a JSON object with a list of available material presets.
- `POST /generate-ai-image/`: Generate an image from a text prompt. Takes a `prompt` query parameter.
- `POST /process-image/`: Upload an image file to get a processed preview image (PNG).
- `POST /generate-gcode/`: Upload an image file to get the generated G-code as plain text. Can optionally take a `preset` query parameter.
- `POST /send-gcode`: Send a JSON payload with `port` and `gcode` to start the engraving process.

## Troubleshooting

### No Serial Ports Found
- **Is your engraver connected and powered on?** Make sure the engraver is properly connected to your computer's USB port and is turned on.
- **Do you have the correct drivers?** Some engravers may require specific drivers to be installed. For the A7 Mini Pro, you may need to find and install the appropriate drivers for your operating system.
- **Permissions issues (Linux/macOS):** Your user may not have permission to access the serial port. You may need to add your user to the `dialout` or `tty` group.

### Engraving Doesn't Start
- **Check the status message:** The status message in the UI may provide information about any errors.
- **Incorrect serial port:** Make sure you have selected the correct serial port for your engraver.
- **Engraver not in a ready state:** Some engravers need to be in a specific state (e.g., "idle") to accept commands. Try resetting your engraver.
