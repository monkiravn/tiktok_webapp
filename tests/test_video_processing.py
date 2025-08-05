"""Tests for video processing functionality."""

import io
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from src.app import create_app
from src.services.video_service import VideoService


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def video_service(app):
    """Create a video service instance."""
    with app.app_context():
        return VideoService()


def test_allowed_file_valid_extensions(video_service):
    """Test that valid video file extensions are accepted."""
    assert video_service.allowed_file("test.mp4") is True
    assert video_service.allowed_file("test.mkv") is True
    assert video_service.allowed_file("test.mov") is True


def test_allowed_file_invalid_extensions(video_service):
    """Test that invalid file extensions are rejected."""
    assert video_service.allowed_file("test.txt") is False
    assert video_service.allowed_file("test.jpg") is False
    assert video_service.allowed_file("test") is False
    assert video_service.allowed_file("") is False


@patch('src.services.video_service.VideoFileClip')
@patch('os.path.getsize')
def test_process_video_success(mock_getsize, mock_video_clip, video_service, app):
    """Test successful video processing."""
    # Mock video clip
    mock_video = MagicMock()
    mock_video.duration = 10.0  # 10 second video
    mock_video.w = 1920
    mock_video.h = 1080
    
    # Mock video operations
    mock_trimmed = MagicMock()
    mock_scaled = MagicMock()
    mock_cropped = MagicMock()
    mock_flipped = MagicMock()
    mock_processed = MagicMock()
    
    mock_video.subclipped.return_value = mock_trimmed
    mock_trimmed.resized.return_value = mock_scaled
    mock_scaled.cropped.return_value = mock_cropped
    mock_cropped.with_effects.return_value = mock_flipped
    mock_flipped.without_audio.return_value = mock_processed
    
    # Mock file writing and size checking
    mock_processed.write_videofile = MagicMock()
    mock_getsize.side_effect = [1024*1024*2, 1024*1024]  # Processed: 2MB, Original: 1MB
    
    mock_video_clip.return_value.__enter__.return_value = mock_video
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_file.write(b"fake video content")
        temp_path = temp_file.name
    
    try:
        with app.app_context():
            result = video_service._process_video(temp_path)
            
            # Verify the result structure
            assert "original_file" in result
            assert "processed_file" in result
            assert "original_duration" in result
            assert "processed_duration" in result
            assert "original_size" in result
            assert "processed_size" in result
            assert "processing_status" in result
            assert result["processing_status"] == "Success"
            
            # Verify specific values
            assert result["original_duration"] == 10.0
            assert result["processed_duration"] == 8.0  # 10 - 2 seconds
            assert result["original_size"] == (1920, 1080)
            assert result["processed_size"] == (1920, 1080)  # Original dimensions maintained after zoom/crop
            assert result["processed_file_size_mb"] == 2.0
            assert result["original_file_size_mb"] == 1.0
            
            # Verify video transformations were called
            mock_video.subclipped.assert_called_once_with(1, 9.0)  # Trim 1 sec from start and end
            mock_trimmed.resized.assert_called_once_with((2112, 1188))  # Scale to 110% before cropping
            mock_scaled.cropped.assert_called_once()  # Crop back to original dimensions
            mock_cropped.with_effects.assert_called_once()  # Horizontal flip
            mock_flipped.without_audio.assert_called_once()  # Remove audio
            mock_processed.write_videofile.assert_called_once()
            
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


@patch('src.services.video_service.VideoFileClip')
def test_process_video_too_short(mock_video_clip, video_service, app):
    """Test processing fails for videos shorter than 2 seconds."""
    # Mock video clip with short duration
    mock_video = MagicMock()
    mock_video.duration = 1.5  # 1.5 second video
    mock_video_clip.return_value.__enter__.return_value = mock_video
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
        temp_file.write(b"fake video content")
        temp_path = temp_file.name
    
    try:
        with app.app_context():
            with pytest.raises(ValueError, match="Video must be longer than 2 seconds"):
                video_service._process_video(temp_path)
                
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_api_upload_no_file(client):
    """Test API upload endpoint with no file."""
    response = client.post('/api/v1/upload')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "No file provided" in data["error"]


def test_api_health(client):
    """Test API health endpoint still works."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


@patch('src.services.video_service.VideoFileClip')
@patch('os.path.getsize')
def test_api_upload_integration(mock_getsize, mock_video_clip, client, app):
    """Test full API upload integration with video processing."""
    # Mock video clip for integration test
    mock_video = MagicMock()
    mock_video.duration = 5.0  # 5 second video
    mock_video.w = 640
    mock_video.h = 480
    
    # Mock video operations chain
    mock_trimmed = MagicMock()
    mock_scaled = MagicMock()
    mock_cropped = MagicMock()
    mock_flipped = MagicMock()
    mock_processed = MagicMock()
    
    mock_video.subclipped.return_value = mock_trimmed
    mock_trimmed.resized.return_value = mock_scaled
    mock_scaled.cropped.return_value = mock_cropped
    mock_cropped.with_effects.return_value = mock_flipped
    mock_flipped.without_audio.return_value = mock_processed
    
    # Mock file operations
    mock_processed.write_videofile = MagicMock()
    mock_getsize.side_effect = [1024*1024, 512*1024]  # Processed: 1MB, Original: 0.5MB
    
    mock_video_clip.return_value.__enter__.return_value = mock_video
    
    # Create fake file data
    fake_video_data = b"fake video content for testing"
    
    with app.app_context():
        response = client.post(
            '/api/v1/upload',
            data={'file': (io.BytesIO(fake_video_data), 'test_video.mp4')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "result" in data
        
        result = data["result"]
        assert result["processing_status"] == "Success"
        assert result["original_duration"] == 5.0
        assert result["processed_duration"] == 3.0  # 5 - 2 seconds
        assert result["original_size"] == [640, 480]
        assert result["processed_size"] == [640, 480]  # Original dimensions maintained after zoom/crop
        assert "zoomed in 110%" in result["message"]
        assert "flipped horizontally" in result["message"]
        assert "trimmed 2 seconds" in result["message"]
        assert "audio removed" in result["message"]