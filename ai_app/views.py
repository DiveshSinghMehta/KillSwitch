from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
import redis

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


@api_view(["POST"])
@permission_classes([IsAdminUser])
def kill_service(request):
    return _write_global_state("KILLED")


@api_view(["GET"])
@permission_classes([IsAdminUser])
def kill_status(request):
    from .kill_switch import get_kill_state
    try:
        state = get_kill_state()
    except redis.RedisError:
        return Response({"error": "Redis is unavailable; state cannot be read."}, status=503)
    return Response({"state": state})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def reset_service(request):
    return _write_global_state("ENABLED")


def _write_global_state(state):
    from .kill_switch import set_kill_state
    try:
        set_kill_state(state)
    except redis.RedisError:
        return Response({"error": "Redis is unavailable; state was not changed."}, status=503)
    return Response({"state": state})
