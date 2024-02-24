import requests
import PyPDF2
import os

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

from openai import OpenAI
from urllib.parse import urlsplit
from decouple import config

# e.g: /extract/parseFile/?url=....sample-new-fidelity-acnt-stmt.pdf
def parseFile(request):
    fileUrl = request.GET.get('url', None)
    urlPath = urlsplit(fileUrl).path
    filePath = os.path.basename(urlPath) 

    if os.path.isfile(filePath):
        print(f"File {filePath} existed.")
    else:
        response = requests.get(fileUrl)
        if response.status_code == 200:
            with open(filePath, "wb") as file:
                file.write(response.content)
            print(f"File {filePath} downloaded successfully.")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
            return HttpResponse("Failed to download file!")

    extractedOutput = extractInformationFromFile(filePath)    

    return HttpResponse(extractedOutput, content_type="text/plain")

ENTITIES = ["account owner name", "portfolio value", "name/cost basis of all holdings"]
def extractInformationFromFile(filePath):
    openai_api_key = config('OPENAI_API_KEY')

    # Read the content of the saved file
    pdfContent = readPdf(filePath)

    # Use OpenAI API to extract information from the PDF
    prompt = f"From the statement:\n{pdfContent}\nIn JSON format, extract all of following entities: "
    for entity in ENTITIES:
        prompt += entity + ", "

    client = OpenAI(
        api_key=openai_api_key
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "user", 
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

def readPdf(filePath):
    with open(filePath, 'rb') as file:
        pdfReader = PyPDF2.PdfReader(file)
        numPages = len(pdfReader.pages)

        text = ""
        for pageNumber in range(numPages):
            page = pdfReader.pages[pageNumber]
            text += page.extract_text()
    return text