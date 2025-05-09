# MovRec - Movie Recommendation System

MovRec is a sophisticated movie recommendation system built with ASP.NET Core and Python, combining the power of machine learning with a modern web interface to provide personalized movie recommendations to users.

## Features

- User authentication and authorization
- Personalized movie recommendations
- Genre-based filtering
- User rating system
- Email verification system
- Responsive web interface
- Machine learning-based recommendation engine

## Technology Stack

### Backend
- ASP.NET Core (C#)
- Entity Framework Core
- PostgreSQL Database
- Python (for ML components)
- PyTorch
- NumPy
- Pandas

### Frontend
- ASP.NET Core MVC
- HTML/CSS/JavaScript
- Bootstrap

## Prerequisites

- .NET 7.0 or later
- Python 3.8 or later
- PostgreSQL
- Visual Studio 2022 or VS Code

## Installation

1. Clone the repository:
```bash
<<<<<<< HEAD
git clone [https://github.com/YousefKayyali/MovRec.git]
=======
git clone [repository-url]
>>>>>>> 79054dc (added a  readme file to show how to run the project)
cd MovRec
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Build and run the application:
>>>>>>> 79054dc (added a  readme file to show how to run the project)
```bash
dotnet build
dotnet run
```

## Project Structure

- `Controllers/` - ASP.NET Core controllers
- `Models/` - Data models and entities
- `Views/` - MVC views
- `Services/` - Business logic services
- `AiModel/` - Python-based ML models
- `data/` - Database context and migrations
- `wwwroot/` - Static files (CSS, JS, images)
- `Helpers/` - Utility classes and helpers
- `Filters/` - Custom action filters

## Machine Learning Components

The project includes several Python-based ML components:
- `user_to_user_lr.py` - User-to-user collaborative filtering
- `model.py` - Core recommendation model
- `after_rating.py` - Post-rating analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

