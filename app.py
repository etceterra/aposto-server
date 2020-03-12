import subprocess
import base64
from time import time
from datetime import datetime
import requests
from requests import Response as requests_Response
from dotenv import load_dotenv
import os
from typing import List, Dict
from pystrich.datamatrix import DataMatrixEncoder

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, FileResponse, UJSONResponse
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import ujson

load_dotenv()
SEND_IN_BLUE_API_KEY = os.getenv("SEND_IN_BLUE_API_KEY")

with open("config.json", "r") as configData:
    ENV = os.getenv("ENV")
    fullConfig: Dict = ujson.load(configData)
    config: Dict = fullConfig["PROD"] if ENV == "PROD" else fullConfig["DEV"]

middleware: List[Middleware] = [
    Middleware(CORSMiddleware, allow_origins=[config["apostoAppURL"]])
]

app: Starlette = Starlette(debug=True, middleware=middleware)


@app.route("/pdf/{receipt_content_base_64}/{name}")
async def downloadReceipt(request: Request):
    generateReceipt(request.path_params["receipt_content_base_64"])

    return FileResponse("out.pdf")


@app.route("/email/{receipt_content_base_64}")
async def emailReceipt(request: Request):
    receipt_content: Dict = ujson.loads(
        base64.b64decode(request.path_params["receipt_content_base_64"]).decode(
            "latin1"
        )
    )
    receipt_filename: str = f"facture-{round(time())}.pdf"

    generateReceipt(request.path_params["receipt_content_base_64"])

    with open("out.pdf", "rb") as receipt_file:
        receipt_file_base_64 = base64.b64encode(receipt_file.read())

    data: str = ujson.dumps(
        {
            "sender": {"email": "facture@app.aposto.ch", "name": "Aposto"},
            "to": [
                {
                    "email": receipt_content["customer"]["email"],
                    "name": f"{receipt_content['customer']['firstName']} {receipt_content['customer']['lastName']}",
                }
            ],
            "bcc": [
                {
                    "email": receipt_content["author"]["email"],
                    "name": receipt_content["author"]["name"],
                }
            ],
            "htmlContent": f"<h1>Votre facture</h1><p>Bonjour {receipt_content['customer']['firstName']} {receipt_content['customer']['lastName']},</p><p>Vous pouvez dès à présent consulter votre facture du {datetime.now().strftime('%d/%m/%Y')} en pièce jointe.</p><p>À très bientôt,<br>{receipt_content['author']['name']}</p>",
            "subject": "Aposto - Votre nouvelle facture",
            "attachment": [{"content": receipt_file_base_64, "name": receipt_filename}],
        }
    )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": SEND_IN_BLUE_API_KEY,
    }

    response: requests_Response = requests.post(
        f"{config['sendInBlueAPIURL']}/smtp/email", data=data, headers=headers
    )

    if response.status_code == 201:
        return UJSONResponse()

    response_content: Dict = ujson.loads(response.text)

    return UJSONResponse(response_content, status_code=HTTP_400_BAD_REQUEST)


@app.route("/datamatrix/{datamatrix_str}/datamatrix.png")
async def dataMatrix(request: Request):
    decoded_data_matrix_st: str = base64.b64decode(
        request.path_params["datamatrix_str"]
    ).decode()
    encoder: DataMatrixEncoder = DataMatrixEncoder(decoded_data_matrix_st)

    encoder.save("datamatrix.png")

    return FileResponse("datamatrix.png")


@app.route("/favicon.ico")
async def icon(request: Request):
    return RedirectResponse("https://terrapeute.ch/img/favicon.png")


def generateReceipt(receipt_content_base_64: str):
    receipt_url: str = f"https://app.aposto.ch/receipt/receipt.html?receiptContent={receipt_content_base_64}"

    subprocess.Popen(f"npx electron-pdf {receipt_url} out.pdf", shell=True)
