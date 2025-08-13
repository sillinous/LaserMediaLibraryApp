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
+------------------+      +-----------------+      +--------------------+
|  Frontend Client | <--> |   API Gateway   | <--> |    User Service    |
| (React/Mobile)   |      | (Routing/Auth)  |      |   (PostgreSQL)     |
+------------------+      +-------+---------+      +--------------------+
                                  |
                   +--------------+--------------+
                   |              |              |
+------------------v--+  +---------v-------+  +---v---------------+
|   Media Service   |  |  Product Service  |  |   Order Service   |
| (Object Store/AI) |  |   (PostgreSQL)    |  |   (PostgreSQL)    |
+-------------------+  +-------------------+  +-------------------+
                   |              |              |
                   |      +-------v-------+      |
                   |      | Event Bus /   |      |
                   |      | Message Queue | <----+
                   |      +-------+-------+      |
                   |              |              |
+------------------v--+  +---------v-------+      |
|    AI Service     |  |  Engraver Service | <----+
| (Image Gen/NLP)   |  | (Bluetooth/WiFi)  |
+-------------------+  +-------------------+

```

### Service Descriptions:

- **Frontend Client:** The user-facing application built with a mobile-first philosophy. It will be a Single Page Application (SPA).
- **API Gateway:** The single entry point for all client requests. It handles routing, authentication, rate limiting, and aggregates responses from various services.
- **User Service:** Manages user identity, authentication (e.g., JWT), authorization, roles, and profiles.
- **Media Service:** Responsible for uploading, storing, processing (grayscale, inversion, background removal, vectorization), and managing all media assets. It will interact with the AI Service for complex tasks.
- **Product Service:** Manages the catalog of engravable products, including their dimensions, materials, and sourcing information.
- **Order Service:** Handles the entire lifecycle of a customer order, from cart to payment to fulfillment status.
- **Engraver Service:** The bridge between the digital platform and the physical world. It translates the final design into machine-specific commands and communicates with laser engravers via protocols like Bluetooth or WiFi.
- **AI Service:** A centralized hub for computationally intensive AI tasks. This includes AI image generation (e.g., text-to-image), natural language processing for user commands, and advanced image analysis.
- **Event Bus:** An asynchronous messaging backbone (e.g., RabbitMQ, Kafka) that allows services to communicate in a decoupled manner. For example, when an order is `created`, the Order Service publishes an event, and the Engraver Service and Notification Service can subscribe and react to it.

## 4. Data Storage

We will use a polyglot persistence approach:

- **PostgreSQL:** A robust relational database for structured data such as users, products, and orders. Its support for JSONB also provides flexibility.
- **Object Storage (S3/MinIO):** A scalable and cost-effective solution for storing large binary files, primarily the images and media assets in the Media Library.

This architecture provides a solid, scalable, and flexible foundation upon which to build the platform.

## 5. Proposed Technology Stack

This section details the specific technologies chosen for the initial implementation of the platform.

- **Frontend:**
    - **Framework:** **React (with Vite)**
    - **Justification:** React's component-based architecture is ideal for building a complex, maintainable UI. Its vast ecosystem of libraries and strong community support will accelerate development. Vite provides an extremely fast build and development experience.
    - **Styling:** **Tailwind CSS** for a utility-first approach that enables rapid, responsive, and consistent design.

- **Backend:**
    - **Framework:** **Python with FastAPI**
    - **Justification:** Python is the de facto language for AI/ML, giving us direct access to a rich ecosystem of libraries (OpenCV, Pillow, scikit-learn, PyTorch, etc.). FastAPI is a modern, high-performance web framework that supports asynchronous programming out of the box, which is crucial for building scalable and responsive services.

- **Database:**
    - **Relational:** **PostgreSQL**
    - **Justification:** PostgreSQL is a powerful, reliable, and open-source object-relational database system. It's well-suited for the structured data of our User, Product, and Order services. Its performance and feature set (like JSONB support) are excellent.
    - **Object Storage:** **MinIO (S3-compatible)**
    - **Justification:** For our media library, a dedicated object storage solution is more scalable and cost-effective than storing blobs in a relational database. MinIO provides an S3-compatible API and is easy to self-host for local development.

- **Infrastructure & Deployment:**
    - **Containerization:** **Docker & Docker Compose**
    - **Justification:** Docker allows us to package each microservice with its dependencies into a portable container. Docker Compose then enables us to define and run our entire multi-container application stack with a single command, ensuring a consistent environment from development to production.
    - **Event Bus:** **RabbitMQ**
    - **Justification:** RabbitMQ is a mature, widely adopted, and reliable message broker. It is perfect for managing asynchronous communication between our microservices, enhancing the resilience and decoupling of the system.
