from django.urls import path
from . import views

urlpatterns = [
    path('stream/<str:room_name>/', views.stream, name='stream'),
    path('start_stream/<str:session_id>/', views.start_stream_view, name='start_stream'),
    path('stop_stream/<str:session_id>/', views.stop_stream_view, name='stop_stream'),
]


# from django.conf.urls.static import static
# from django.urls import path
# from home import views
# from stream import settings
#
# urlpatterns = [
#     path('', views.homepage, name='homepage'),
#     path('stream/<str:room_name>/', views.stream_video, name='stream_video'),
#     path('create-room/', views.create_room, name='create_room'),
#     path('capture-video/', views.capture_video, name='capture_video'),
#     path('capture_video/start/', views.start_video_capture, name='start_video_capture'),
#     path('stop_video_capture/', views.stop_video_capture, name='stop_video_capture'),
#     path('start_rtmp_stream/', views.start_rtmp_stream, name='start_rtmp_stream'),
#     path('view_stream/<str:room_name>/', views.view_stream, name='view_stream'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

