# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from cvg_sdk.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from cvg_sdk.model.audio import Audio
from cvg_sdk.model.audio_all_of import AudioAllOf
from cvg_sdk.model.confidence import Confidence
from cvg_sdk.model.dialog_phase import DialogPhase
from cvg_sdk.model.dtmf import Dtmf
from cvg_sdk.model.dtmf_all_of import DtmfAllOf
from cvg_sdk.model.recording_id import RecordingId
from cvg_sdk.model.recording_objects_response import RecordingObjectsResponse
from cvg_sdk.model.speaker import Speaker
from cvg_sdk.model.text import Text
from cvg_sdk.model.text_all_of import TextAllOf
from cvg_sdk.model.transcript import Transcript
from cvg_sdk.model.transcript_entry import TranscriptEntry
from cvg_sdk.model.transcript_v1 import TranscriptV1
from cvg_sdk.model.transcript_v1_all_of import TranscriptV1AllOf
from cvg_sdk.model.voice import Voice
from cvg_sdk.model.voice_all_of import VoiceAllOf
