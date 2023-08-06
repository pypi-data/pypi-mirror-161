#!pip3 install -U amazon-transcribe
from . import s3
import os
from ...misc import wavefile
from functools import partial
import tempfile
import moviepy.editor as mp
import time
import boto3

transcribe = boto3.client ('transcribe')

def get_duration (s):
    clip = mp.VideoFileClip (s)
    return clip.duration

def extract_wave (s, t, sr = 16000):
    clip = mp.VideoFileClip (s)
    clip.audio.write_audiofile (t, ffmpeg_params = f"-ar {sr} -ac 1".split (), logger = None)

def jobs ():
    existed_jobs = transcribe.list_transcription_jobs ()
    return existed_jobs ['TranscriptionJobSummaries']

def exists (job_name):
    job_verification = True
    for job in jobs ():
        if job_name == job ['TranscriptionJobName']:
            return True
    return False

def async_transcribe (job_name, media_uri, lang = 'ko-KR', max_speakers = 5):
    if max_speakers:
        assert 2 <= max_speakers <= 10,  "Maximum detected speakers is 2 ~ 10"

    if exists (job_name):
        return job_name

    if max_speakers:
        settings = {'ShowSpeakerLabels': True }
        settings ['MaxSpeakerLabels'] = max_speakers

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaSampleRateHertz = 16000,
        MediaFormat = 'wav',
        LanguageCode = lang,
        Subtitles = {"Formats": ["srt"]},
        Settings = settings)

    return job_name

def maybe_completed (job_name):
    result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    progress = result ['TranscriptionJob']['TranscriptionJobStatus']
    if progress in ('COMPLETED', 'FAILED'):
        if progress == 'FAILED':
            return True, None, result ['TranscriptionJob']["FailureReason"]
        jsonuri = result ['TranscriptionJob']['Transcript']['TranscriptFileUri']
        try:
            srturl = result ['TranscriptionJob']['Subtitles']['SubtitleFileUris'][0]
        except:
            srturl = None
        return True, jsonuri, srturl
    return False, None, None
