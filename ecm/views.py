import json
import pandas as pd
from werkzeug.exceptions import BadRequest
from .simulator import (
    ModelContext,
    Simulator,
    SimulatorError,
    modelExtendedLatex,
    computeExtraColumns,
)
from flask import Blueprint, request, send_from_directory, Response, send_file
from .models import Model
from . import schemas

bp = Blueprint("ecm", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
def home():
    return send_file("../static/index.html")


@bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        "../static/", "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@bp.route("/static/<path:path>")
def serve_javascript(path):
    return send_from_directory("../static/", path)


@bp.errorhandler(SimulatorError)
def handle_error(error):
    return {"error": error.args[1]}, 400


@bp.errorhandler(schemas.ValidationError)
def handle_error(error):
    # flake8:noqa
    return {"error": "\n".join(e["msg"] for e in error.errors())}, 400


@bp.route("/api/models/", methods=["GET"])
def list_models():
    models = Model.query.all()
    out = []
    for m in models:
        obj = schemas.Model.from_orm(m)
        out.append(modelExtendedLatex(obj))
    return Response(json.dumps({"models": out}), mimetype="application/json")


@bp.route("/simulate/<int:model_id>", methods=["POST"])
def simulate(model_id):
    data = request.json
    model = Model.query.get(model_id)
    modelSchema = schemas.Model.from_orm(model)
    context = ModelContext(modelSchema)
    sim = Simulator(context)
    if not data:
        raise BadRequest(description="No input data")

    simulationSchema = schemas.Simulation(**data)
    response = {}

    result = sim.simulate(simulationSchema)
    computeExtraColumns(context, result)
    if result.isIterated:
        response["type"] = "multiple"
        response["param"] = {"name": result.param, "values": list(result.paramValues)}
        response["frames"] = []
        for frame in result.frames:
            df = pd.DataFrame(
                data=frame, columns=result.compartments, index=result.timeline
            )
            response["frames"].append(df.transpose().to_dict(orient="split"))
    else:
        response["type"] = "simple"
        df = pd.DataFrame(
            data=result.frames[0], columns=result.compartments, index=result.timeline
        )
        response["frame"] = df.transpose().to_dict(orient="split")

    return Response(json.dumps(response), mimetype="application/json")
