# 🐍 FastAPI Backend Challenge — Milestone 1

## 📘 Overview

This challenge is designed to evaluate your ability to:
- Build a backend API using **FastAPI** with **PostgreSQL** as the backend database.
- Write unit tests to validate functionality.
- Containerize the entire application using **Docker**.

Do your best coding — we will review and discuss your implementation together.

---

## 🚩 Milestone 1.1 — Basic CRUD API

In our company, we have a set of IoT sensors connected to several units.  
Our admin team needs to view, validate, and archive data received from these sensors.  
They also need an overview of each unit’s statistics.

You are asked to design and implement an API that supports this solution.

### Requirements:

- Use **PostgreSQL** as the backend database.  
- **Do not use an ORM** — implement database access using the **Repository Pattern**.  
- Implement complete CRUD endpoints for the required entities.  
- Apply clean code and solid design principles; your implementation quality will be reviewed and discussed.

---

## 🚩 Milestone 1.2 — API Documentation

Ensure that the API is documented using **OpenAPI**.

### Requirements:

- The Swagger UI endpoint (e.g., `/docs`) must be accessible.  
- All endpoints and models should include appropriate descriptions, request/response schemas, and status codes.

---

## 🚩 Milestone 1.3 — Unit Testing

Write unit tests that validate the API’s functionality.  
Your API should also be testable using JSON input.

### Requirements:

- Use a testing framework such as **pytest** or **unittest**.  
- Use **fixtures**, **mocking**, or a **test database** to isolate tests from production data.  
- Cover positive and negative test cases for the main business logic.

---

## 🚩 Milestone 1.4 — Dockerization

Containerize your application using **Docker**.

### Requirements:

- Include a `Dockerfile` that builds and runs the FastAPI application.  
- Include a `docker-compose.yml` file to start both the FastAPI service and the PostgreSQL database.  
- The app and database should communicate via **Docker networking**.  
- Use **environment variables** for configuration (database credentials, ports, etc.).  
- The entire project should be runnable in a fully containerized environment.  
- Provide **sample data** to initialize the app on startup.

---

## 🧩 Deliverables

At the end of Milestone 1, you should provide:

- Source code of the FastAPI application  
- CRUD endpoint implementations  
- PostgreSQL integration via repository pattern  
- Unit test files  
- Dockerfile and docker-compose.yml  
- A clear `README.md` with setup and usage instructions  

---

## ✅ Evaluation Criteria

Your submission will be evaluated based on:

- **Architecture & Design:** Use of clean code, repository pattern, and separation of concerns  
- **Problem Solving:** Logical data modeling and domain-driven design approach  
- **Code Quality:** Readability, maintainability, and adherence to best practices  
- **Testing:** Coverage, clarity, and robustness of unit tests  
- **Dockerization:** Proper setup, configuration, and startup flow  
- **Documentation:** Clear explanation of setup, API usage, and design rationale  

---

## 🎯 Goal

By completing this milestone, you should deliver a **functional, well-structured, and maintainable** FastAPI application that:  
- Interacts with a PostgreSQL database via repository abstraction  
- Exposes CRUD APIs to manage IoT sensor data and unit information  
- Includes automated tests and Docker-based deployment  

---

**Good luck — write clean, thoughtful, and production-grade code!**
