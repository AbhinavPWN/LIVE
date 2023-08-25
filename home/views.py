import uuid

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


def stream(request, room_name):
    session_id = str(uuid.uuid4())  # Generate a unique session ID
    response = render(request, 'home/stream.html', {'room_name': room_name})
    response.set_cookie('stream_session_id_' + room_name, session_id)  # Set the session ID as a cookie
    return response


def clear_session_cookie(request, room_name):
    response = HttpResponse("Session cookie cleared.")
    response.delete_cookie('stream_session_id_' + room_name)
    return response


def render_stream(request, room_name):
    return render(request, 'home/stream_renderer.html', {'room_name': room_name})


async def start_stream(session_id):
    channel_layer = get_channel_layer()
    await channel_layer.group_add(session_id, "video_group_" + session_id)
    await channel_layer.group_send("video_group_" + session_id, {
        "type": "video.start",
    })


async def stop_stream(session_id):
    channel_layer = get_channel_layer()
    await channel_layer.group_discard(session_id, "video_group_" + session_id)
    await channel_layer.group_send("video_group_" + session_id, {
        "type": "video.stop",
    })


async def start_stream_view(request, session_id):
    await start_stream(session_id)  # Await the asynchronous function
    return JsonResponse({'message': 'Stream started'})


async def stop_stream_view(request, session_id):
    await stop_stream(session_id)  # Await the asynchronous function
    return JsonResponse({'message': 'Stream stopped'})
