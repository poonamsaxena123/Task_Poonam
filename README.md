# Event Management API Task

## Overview
Develop a RESTful API using **Django**, **Django REST Framework (DRF)**, and **Python Core** to manage events, user participation, invitations, and feedback.

## Requirements

### 1. Models & Relationships

#### **User (Default Django User Model)**

#### **Event**
- `title` (CharField)
- `description` (TextField)
- `host` (ForeignKey to User, related_name="hosted_events")
- `start_time` (DateTimeField)
- `end_time` (DateTimeField)
- `location` (CharField)
- `max_participants` (IntegerField)
- `created_at` (DateTimeField, auto_now_add=True)

#### **EventParticipant**
- `user` (ForeignKey to User)
- `event` (ForeignKey to Event)
- `joined_at` (DateTimeField, auto_now_add=True)
- Unique constraint on (`user`, `event`)

#### **Invitation**
- `event` (ForeignKey to Event)
- `inviter` (ForeignKey to User, related_name="sent_invitations")
- `invitee` (ForeignKey to User, related_name="received_invitations")
- `status` (ChoiceField: `PENDING`, `ACCEPTED`, `DECLINED`)
- `sent_at` (DateTimeField, auto_now_add=True)
- `responded_at` (DateTimeField, null=True, blank=True)

#### **Feedback**
- `event` (ForeignKey to Event)
- `user` (ForeignKey to User)
- `rating` (IntegerField, choices 1-5)
- `comment` (TextField, optional)
- `created_at` (DateTimeField, auto_now_add=True)

## 2. API Endpoints

### **Authentication**
- `POST /api/register/` → Register user
- `POST /api/login/` → Obtain JWT token

### **Event Management**
- `POST /api/events/` → Create an event (Authenticated users only)
- `GET /api/events/` → List events (Filter: by `host`, `date range`, and `location`)
- `GET /api/events/{id}/` → Retrieve a specific event
- `PUT /api/events/{id}/` → Update an event (Only host)
- `DELETE /api/events/{id}/` → Delete an event (Only host)

### **Event Participation**
- `POST /api/events/{id}/register/` → Register for an event (Check max participants)
- `GET /api/events/{id}/participants/` → List participants
- `DELETE /api/events/{id}/unregister/` → Remove self from event

### **Invitations**
- `POST /api/events/{id}/invite/` → Send an invitation (Only host can invite)
- `GET /api/invitations/` → List invitations for the logged-in user
- `PUT /api/invitations/{id}/` → Accept or decline an invitation

### **Feedback**
- `POST /api/events/{id}/feedback/` → Leave feedback (Only participants)
- `GET /api/events/{id}/feedback/` → List feedback for an event

## 3. Additional Features

### **Permissions & Validation**
- Only event hosts can edit/delete their events.
- Users cannot register twice for the same event.
- Max participants check before registering.
- Users can leave feedback only if they attended the event.

### **Filters**
- Events should be filterable by:
  - `host`
  - `date range` (`start_time` and `end_time`)
  - `location`

### **Pagination**
- List of events, participants, and feedback should be paginated.

### **Database Constraints**
- Unique constraint on (`user`, `event`) for registrations and feedback.

### **Throttling**
- Limit event creation to **5 per day per user**.
- Limit feedback posting to **1 per event per user**.

## 4. features
- **Custom Management Command**: Delete events older than **1 month**.
- **WebSockets (Optional)**: Notify users in real-time when an invitation is received.

## 5. Expected Deliverables
- Django + DRF project with:
  - `models.py` (Correct relationships & constraints)
  - `serializers.py` (Data validation)
  - `views.py` (Using `APIView`/`ViewSet`)
  - `urls.py` (Correct routing)
  - `permissions.py` (Access control)
  - **Unit tests covering APIs**

