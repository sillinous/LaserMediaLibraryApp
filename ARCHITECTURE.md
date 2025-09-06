# Architectural Blueprint: AI-Centric Laser Engraving Platform

This document outlines the high-level architecture for the AI-centric laser engraving platform. It is a living document and will evolve as the project progresses.

## 1. Guiding Principles

The architecture is designed with the following principles in mind:

- **AI-First:** Core workflows, from design to business management, will be enhanced and driven by Artificial Intelligence.
- **Highly Modular & Scalable:** The system is composed of independent, loosely-coupled services that can be developed, deployed, and scaled individually.
- **Technology Agnostic:** The microservices approach allows individual services to be built with the best technology for the job, facilitating future innovation and integration.
- **Mobile-First:** The user interface will be designed for a seamless experience on mobile devices first, then adapted for larger screens.
- **Intuitive & Abstracted:** The complexity of the engraving process and business management will be abstracted away from the user, providing a simple, guided experience.
- **Extensible:** The architecture will support a "plug-and-play" model for adding new features, integrations, and extensions.

## 2. Architectural Pattern: Microservices

We will use a **microservices architecture**. This pattern aligns perfectly with our guiding principles. It involves breaking down the application into a suite of small, independent services that communicate with each other over a network.

**Benefits:**
- **Flexibility:** Each service can be written in a different language or use a different data store.
- **Resilience:** Failure in one service is less likely to cause a total system failure.
- **Scalability:** We can scale individual services based on demand (e.g., scale the Media Service during peak upload times).
- **Maintainability:** Smaller codebases are easier to understand, manage, and update.

## 3. Core Services & Components

Below is a diagram and description of the initial set of services.

```
+------------------+      +----------------------+      +--------------------+
|  Frontend Client | <--> |    Media Service     | <--> |   OpenAI API       |
| (React SPA)      |      | (FastAPI, PySerial)  |      | (External Service) |
+------------------+      +----------------------+      +--------------------+
```

### Service Descriptions:

- **Frontend Client:** A React-based Single Page Application (SPA) that provides the user interface for controlling the laser engraver. It allows the user to upload an image, select a serial port, and initiate the engraving process.
- **Media Service:** A Python FastAPI backend that provides the core logic for the application. Its responsibilities include:
    - Generating images from text prompts by calling the OpenAI API.
    - Processing uploaded images (converting to grayscale, inverting).
    - Generating G-code from the processed images.
    - Managing and serving material presets (e.g., for wood, leather).
    - Communicating with the laser engraver over a serial connection to send the G-code.
    - Listing available serial ports.
- **OpenAI API:** An external service used for generating images from text prompts.

## 4. Data Storage

The application does not currently use a database or any persistent data storage. All data is processed in memory.

## 5. Note on A7 Mini Pro Engraver

The current implementation assumes a generic laser engraver that accepts G-code over a standard serial connection. The G-code generation and communication protocols have been implemented based on common standards (like GRBL) but have **not** been tested on an A7 Mini Pro device. The following assumptions have been made:

- The engraver uses a standard serial/USB connection.
- The engraver communicates at a baud rate of 115200.
- The engraver understands standard G-code commands for movement (`G0`, `G1`) and laser control (`M4`, `M5`).

Further testing and possible adjustments to the G-code generation and serial communication settings may be required to ensure compatibility with the A7 Mini Pro.

## 6. Technology Stack

- **Frontend:**
    - **Framework:** **React (with Vite)**
    - **Styling:** Default CSS.

- **Backend:**
    - **Framework:** **Python with FastAPI**
    - **Libraries:**
        - **Pillow:** For image processing.
        - **PySerial:** For serial communication with the engraver.

- **Infrastructure & Deployment:**
    - **Containerization:** **Docker & Docker Compose**
