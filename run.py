import os
from datetime import datetime
from src.app import create_app

app = create_app()

# Add template context processor for current year
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    # Use this for development only
    app.run(debug=True)
