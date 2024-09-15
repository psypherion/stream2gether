import os
from typing import Optional, AsyncIterable
import aiofiles
from starlette.requests import Request
from starlette.responses import StreamingResponse


class VideoStreamer:
    ALLOWED_EXTENSIONS: set[str] = {'mp4', 'mkv', 'webm', 'avi', 'mov', 'vid'}

    def __init__(self, video_path: str):
        self.video_path = video_path
        self.check_file_extension()

    def check_file_extension(self) -> None:
        _, ext = os.path.splitext(self.video_path)
        ext = ext.lstrip('.').lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

    async def stream_video(self, request: Request) -> StreamingResponse:
        file_size = os.path.getsize(self.video_path)
        range_header = request.headers.get('range')

        if range_header:
            start, end = self.parse_range_header(range_header, file_size)
            if end is None:
                end = file_size - 1

            async def file_generator(start: int, end: int) -> AsyncIterable[bytes]:
                async with aiofiles.open(self.video_path, 'rb') as f:
                    await f.seek(start)
                    while start <= end:
                        chunk = await f.read(1024 * 1024)  # Read in 1 MB chunks
                        if not chunk:
                            break
                        start += len(chunk)
                        yield chunk

            content_range = f'bytes {start}-{end}/{file_size}'
            headers = {
                'Content-Range': content_range,
                'Accept-Ranges': 'bytes',
                'Content-Length': str(end - start + 1),
                'Content-Type': 'video/mp4'
            }
            return StreamingResponse(file_generator(start, end), headers=headers, status_code=206)
        else:
            async def file_generator() -> AsyncIterable[bytes]:
                async with aiofiles.open(self.video_path, 'rb') as f:
                    while chunk := await f.read(1024 * 1024):  # Read in 1 MB chunks
                        yield chunk

            headers = {
                'Content-Length': str(file_size),
                'Content-Type': 'video/mp4'
            }
            return StreamingResponse(file_generator(), headers=headers)

    def parse_range_header(self, range_header: str, file_size: int) -> tuple[int, Optional[int]]:
        byte_range = range_header.strip().split('=')[1]
        start_end = byte_range.split('-')
        start = int(start_end[0])
        end = int(start_end[1]) if start_end[1] else None
        return start, end
