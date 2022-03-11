from app import create_app, db

if __name__ == "__main__":
    app = create_app("default")

    app_context = app.app_context()
    app_context.push()
    db.create_all()

    app.run(debug=True, port="5000")
