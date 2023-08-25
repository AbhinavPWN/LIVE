import json
import subprocess
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio


class VideoConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream_sessions = {}  # Dictionary to hold WebSocket connections
        self.room_name = None
        self.room_group_name = None
        self.session_id = None
        self.ffmpeg_process = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_group_{self.room_name}'
        self.session_id = None

        await self.accept()

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the dictionary
        if self.session_id in self.stream_sessions:
            self.stream_sessions.pop(self.session_id)

        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Terminate the FFmpeg process if it's running
        if self.ffmpeg_process is not None:
            self.ffmpeg_process.terminate()
            await self.ffmpeg_process.wait()
            self.ffmpeg_process = None

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            try:
                text_data_json = json.loads(text_data)
                self.session_id = text_data_json['session_id']

                # Add the WebSocket connection to the dictionary
                self.stream_sessions[self.session_id] = self.channel_name

                # Join the room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

                # Start sending video frames to all connected clients
                # await self.send_video_frames(self.session_id)

                # Broadcast the session ID to other tabs
                await self.broadcast_session_id(self.session_id)

            except Exception as e:
                print('Error:', e)

    async def video_frame(self, event):
        # This method will send video frames to all connected clients in the group
        frame_data = event['data']

        # Send the video frame as binary data to the client
        await self.send(bytes_data=frame_data)

    async def send_video_frame(self, frame_data):
        # Send the frame data to all clients in the group
        await self.send(bytes_data=frame_data)

        # Send the frame data to Nginx RTMP server
        subprocess.run([
            'ffmpeg', '-i', '-', '-c:v', 'copy', '-f', 'flv',
            f'rtmp://localhost/live/stream?session={self.session_id}'
        ], input=frame_data, capture_output=True, shell=False)

    async def broadcast_session_id(self, event):
        session_id = event['session_id']
        await self.send(text_data=session_id)

    async def video_start(self):
        # Start the video stream
        self.ffmpeg_process = await self.start_video_stream()

    async def video_stop(self):
        # Stop the video stream
        await self.stop_video_stream()

    async def start_video_stream(self):
        if self.ffmpeg_process is None:
            session_id = self.session_id
            ffmpeg_cmd = [
                'ffmpeg', '-f', 'v4l2', '-framerate', '30', '-video_size', '1280x720', '-i', '/dev/video0',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'zerolatency',
                '-f', 'flv', f'rtmp://localhost/live/{session_id}'
            ]
            return await asyncio.create_subprocess_exec(*ffmpeg_cmd)

    async def stop_video_stream(self):
        if self.ffmpeg_process is not None:
            self.ffmpeg_process.terminate()
            await self.ffmpeg_process.wait()
            self.ffmpeg_process = None
