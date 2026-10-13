from django.shortcuts import render

from .kill_switch import is_ai_enabled
# from .monitor import monitor_output


# Create your views here.from rest_framework.decorators import api_view

from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Document

from ollama import chat
from langsmith import traceable


@traceable(
    name="KILLSWITCH Ollama Generation",
    metadata={"model": "qwen2.5:3b"}
)
def generate_answer(prompt: str) -> str:
    response = chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]



@api_view(['POST'])
def ask(request):
    # if not is_ai_enabled():
    #     return Response(
    #         {"error": "AI is currently disabled."},
    #         status=503
    #     )

    question = request.data.get("question")

    documents = Document.objects.all()

    context = ""

    for document in documents:
        context += document.content + "\n"

    prompt = f"""
Use the following context to answer the user's question.

Context:
{context}

Question:
{question}

Answer using only the provided context.
"""

    # response = chat(
    #     model="qwen2.5:3b",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt
    #         }
    #     ]
    # )
    answer = generate_answer(prompt)

    # if monitor_output(answer):
    #     return Response(
    #         {"error": "Sensitive information detected. Response blocked."},
    #         status=403
    #     )

    return Response({
        "question": question,
        "answer": answer
    })
    
@api_view(['POST'])
def add_document(request):
    title = request.data.get("title")
    content = request.data.get("content")

    document = Document.objects.create(
        title=title,
        content=content
    )

    return Response({
        "message": "Document added",
        "id": document.id
    })