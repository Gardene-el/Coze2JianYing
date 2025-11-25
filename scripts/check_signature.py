
import inspect
from pyJianYingDraft import VideoSegment, VideoMaterial

print("VideoSegment init signature:")
try:
    print(inspect.signature(VideoSegment.__init__))
except Exception as e:
    print(e)

print("\nVideoMaterial init signature:")
try:
    print(inspect.signature(VideoMaterial.__init__))
except Exception as e:
    print(e)
