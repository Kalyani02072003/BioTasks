from flask import Flask

from backend.routes.antifold import antifold_bp
from backend.routes.protein_mpnn import proteinmpnn_bp
from backend.routes.tasks import tasks_bp
from backend.routes.ligand_mpnn import ligandmpnn_bp
from backend.routes.thompson_sampling import ts_bp
from backend.routes.freewilson import freewilson_bp
app = Flask(__name__)



# Register blueprints
app.register_blueprint(antifold_bp, url_prefix="/v1/api/antifold")
app.register_blueprint(proteinmpnn_bp, url_prefix="/v1/api/proteinmpnn")
app.register_blueprint(tasks_bp, url_prefix="/v1/api/tasks")
app.register_blueprint(ligandmpnn_bp, url_prefix="/v1/api/ligandmpnn")
app.register_blueprint(ts_bp, url_prefix="/v1/api/thompson_sampling")
app.register_blueprint(freewilson_bp, url_prefix="/v1/api/freewilson")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
