# Tuition Management Platform (SaaS)

## Overview
A scalable, full-stack tuition management system built with **Django** and **Docker**. Designed to handle real-world scheduling, billing, and homework workflows for private tutoring businesses.

**Live Demo:** [Insert Render Link Here if available]

## Key Features
* **Role-Based Access Control (RBAC):** Distinct dashboards for Tutors (marking, scheduling), Students (homework submission), and Parents (billing/progress).
* **Automated Scheduling:** Custom booking logic that handles recurring slots, cancellations, and time-zone management.
* **Submission Pipeline:** Homework upload and grading workflow with support for media files.
* **Production Ready:** Containerized with Docker and configured for CI/CD deployment.

## Tech Stack
* **Backend:** Python 3.11, Django 5.0
* **Database:** PostgreSQL (Production), SQLite (Dev)
* **Infrastructure:** Docker, Docker Compose
* **API:** Django REST Framework (DRF)

## Local Setup (Docker)
Get the system running in 2 commands:

```bash
# 1. Build the container
docker-compose build

# 2. Run the server
docker-compose up
Architecture
bookings/: Handles calendar logic and slot reservation.

core/: User authentication and role management.

homework/: Submission handling and file storage logic.

api/: REST endpoints for mobile/frontend integration.