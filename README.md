# Library Management System API Documentation

This documentation provides details about the endpoints available in the Library Management System, their usage, and expected request/response formats.

---

## **Base URL**
`http://127.0.0.1:5000`

---

## **Authentication**
The system uses JWT-based authentication for all protected endpoints. Obtain a token by logging in and include it in the `Authorization` header as:

```
Authorization: Bearer <your_token>
```

---

## **Endpoints**

### **1. User Registration**
- **Endpoint**: `/register`
- **Method**: `POST`
- **Description**: Registers a new user (admin or regular).

#### Request Body:
```json
{
  "email": "admin@example.com",
  "password": "admin123",
  "role": "admin"
}
```
- `email`: User email (required, unique).
- `password`: User password (required).
- `role`: Role of the user (`admin` or `user`). Defaults to `user`.

#### Response:
- **201 Created**:
```json
{
  "message": "User registered successfully"
}
```
- **400 Bad Request** (e.g., email already exists):
```json
{
  "message": "Email already exists"
}
```

---

### **2. User Login**
- **Endpoint**: `/login`
- **Method**: `POST`
- **Description**: Authenticates the user and returns a JWT.

#### Request Body:
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

#### Response:
- **200 OK**:
```json
{
  "access_token": "<JWT_TOKEN>"
}
```
- **401 Unauthorized**:
```json
{
  "message": "Invalid credentials"
}
```

---

### **3. Get Books**
- **Endpoint**: `/books`
- **Method**: `GET`
- **Description**: Retrieves a list of all books in the library.

#### Response:
- **200 OK**:
```json
[
  {
    "id": 1,
    "title": "Book Title",
    "author": "Author Name",
    "quantity": 5
  }
]
```

---

### **4. Submit a Borrow Request**
- **Endpoint**: `/borrow-requests`
- **Method**: `POST`
- **Description**: Submits a request to borrow a book for a specific period.
- **Authorization**: Required.

#### Request Body:
```json
{
  "book_id": 1,
  "start_date": "2024-12-15",
  "end_date": "2024-12-20"
}
```
- `book_id`: ID of the book to borrow (required).
- `start_date`: Start date of the borrowing period (required, format: `YYYY-MM-DD`).
- `end_date`: End date of the borrowing period (required, format: `YYYY-MM-DD`).

#### Response:
- **201 Created**:
```json
{
  "message": "Borrow request submitted"
}
```
- **400 Bad Request** (e.g., book not available):
```json
{
  "message": "Book is already borrowed during this period"
}
```

---

### **5. View Borrow Requests (Admin Only)**
- **Endpoint**: `/borrow-requests`
- **Method**: `GET`
- **Description**: Retrieves all borrow requests.
- **Authorization**: Required (Admin only).

#### Response:
- **200 OK**:
```json
[
  {
    "id": 1,
    "user_id": 2,
    "book_id": 1,
    "start_date": "2024-12-15",
    "end_date": "2024-12-20",
    "status": "pending"
  }
]
```
- **403 Forbidden**:
```json
{
  "message": "Access forbidden"
}
```

---

### **6. Approve/Deny a Borrow Request (Admin Only)**
- **Endpoint**: `/borrow-requests/<int:request_id>`
- **Method**: `PATCH`
- **Description**: Approves or denies a borrow request.
- **Authorization**: Required (Admin only).

#### Request Body:
```json
{
  "status": "approved"
}
```
- `status`: New status of the request (`approved` or `denied`).

#### Response:
- **200 OK**:
```json
{
  "message": "Request updated successfully"
}
```
- **404 Not Found**:
```json
{
  "message": "Request not found"
}
```

---

### **7. Download Borrow History as CSV**
- **Endpoint**: `/download-history`
- **Method**: `GET`
- **Description**: Allows a user to download their borrowing history as a CSV file.
- **Authorization**: Required.

#### Response:
- **200 OK**: CSV file download starts.

#### Example Response File (CSV):
```
Borrow ID,Book Title,Start Date,End Date,Status
1,Book Title,2024-12-15,2024-12-20,Approved
2,Another Book,2024-12-25,2024-12-30,Pending
```
- **401 Unauthorized**:
```json
{
  "message": "Unauthorized access"
}
```

---

## **Error Codes**
- **400**: Bad Request (e.g., invalid or missing parameters).
- **401**: Unauthorized (e.g., missing or invalid JWT token).
- **403**: Forbidden (e.g., user lacks required permissions).
- **404**: Not Found (e.g., resource does not exist).
- **422**: Unprocessable Entity (e.g., invalid input format).

---

## **Notes**
1. All date fields should be in the format `YYYY-MM-DD`.
2. Ensure you include the `Authorization` header for protected endpoints.
3. Use `/register` to create both admin and user accounts by specifying the `role` field.

---


