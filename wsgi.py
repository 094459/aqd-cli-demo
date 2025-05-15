from src.app import create_app
from datetime import datetime

app = create_app()

# Add template context processor for current year
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    app.run()
